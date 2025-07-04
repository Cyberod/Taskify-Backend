from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from fastapi import status, HTTPException


from app.task.models.task_models import Task, TaskStatus, TaskPriority, AssignmentType
from app.task.schemas.task_schemas import TaskCreate, TaskUpdate, TaskOut, TaskClaim, GeneralPoolTaskOut
from app.user.models.user_models import User
from app.project.services import project_service
from app.project.utils.project_utils import recalculate_project_completion
from app.project.utils.permissions import (
    user_has_project_permission,
    ProjectPermission,
    require_project_permission,
)


async def create_task(
        task_data: TaskCreate,
        db: AsyncSession,
        current_user_id: UUID
) -> TaskOut:
    """Create a new task in the database.

        Args:
        task_data (TaskCreate): The data for the new task.
        db (AsyncSession): The database session.
        current_user_id (UUID): The ID of the user creating the task.

        Returns:
        TaskOut: The created task object.
    """
    # verify if project exists and the user has permission to create tasks
    project = await(project_service.get_project_by_id(task_data.project_id, db))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    # check if user can create tasks in the project
    await require_project_permission(
        current_user_id,
        task_data.project_id,
        ProjectPermission.CREATE_TASKS,
        db
    )

    # validate assignment logic
    if task_data.assignment_type == AssignmentType.ADMIN_ASSIGNED:
        if task_data.assignee_id:
            # verify if the assignee exists and has acess to the project
            assignee_has_access = await user_has_project_permission(
                task_data.assignee_id,
                task_data.project_id,
                ProjectPermission.VIEW_ALL_TASKS,
                db
            )
            if not assignee_has_access:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee does not have access to this project."
                )
    elif task_data.assignment_type == AssignmentType.GENERAL_POOL:
        # General pool tasks should not have an assignee
        if task_data.assignee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="General pool tasks cannot have an Initial assignee."
            )
        
    # create the task object
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        assignment_type=task_data.assignment_type,
        status=TaskStatus.NOT_STARTED,
        due_date=task_data.due_date,
        project_id=task_data.project_id,
        created_by_id=current_user_id,
        assignee_id=task_data.assignee_id
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Recalculate project completion after adding the task
    await recalculate_project_completion(task_data.project_id, db)

    # Return with user infor
    return await _enrich_task_with_user_info(task, db)




async def get_task_by_id(
    task_id: UUID, 
    db: AsyncSession, 
    current_user_id: UUID
) -> TaskOut:
    """Retrieve a task by its ID with Permission checking.

        Args:

        task_id (UUID): The ID of the task to retrieve.
        db (AsyncSession): The database session.
        current_user_id (UUID): The ID of the user making the request.

        Returns: 
        Taskout: The task object if found and accessible with user information .
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
    
    await require_project_permission(
        current_user_id,
        task.project_id,
        ProjectPermission.VIEW_ALL_TASKS,
        db
    )
    return await _enrich_task_with_user_info(task, db)


async def get_tasks_by_project(
    project_id: UUID, 
    db: AsyncSession,
    current_user_id: UUID,
    assignment_type: Optional[AssignmentType] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None
) -> list[TaskOut]:
    """Retrieve all tasks associated with a specific project with Optional filtering.

        Args:

        project_id (UUID): The ID of the project to retrieve tasks for.
        db (AsyncSession): The database session.
        current_user_id (UUID): The ID of the current user.
        assignment_type(Oprtional[AssignmentType]): filter by assignment type.
        status (Optional[TaskStatus]): Filter by status
        Priority (Oprtional[TaskPriority]): Filter by priority 

        Returns:
        list[TaskOut]: A list of task objects associated with the project.
    """
    # check permissions
    await require_project_permission(
        current_user_id,
        project_id,
        ProjectPermission.VIEW_ALL_TASKS,
        db
    )

    # Build query with filters
    query = select(Task).where(Task.project_id == project_id)

    if assignment_type:
        query = query.where(Task.assignment_type == assignment_type)
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)

    result = await db.execute(query)
    tasks = result.scalars().all()

    # Enrich with user info
    enriched_tasks = []
    for task in tasks:
        enriched_task = await _enrich_task_with_user_info(task, db)
        enriched_tasks.append(enriched_task)

    return enriched_tasks


async def get_general_pool_tasks(
    project_id: UUID,
    db: AsyncSession,
    current_user_id: UUID,
    priority: Optional[TaskPriority] = None
) -> List[GeneralPoolTaskOut]:
    """
    Get all available tasks from the general pool (unassigned).
    
    Args:
        project_id (UUID): The ID of the project.
        db (AsyncSession): The database session.
        current_user_id (UUID): The ID of the current user.
        priority (Optional[TaskPriority]): Filter by priority.

    Returns:
        List[GeneralPoolTaskOut]: Available tasks that can be claimed.
    """
    # Check permission
    await require_project_permission(
        current_user_id,
        project_id,
        ProjectPermission.CLAIM_TASKS,
        db
    )
    
    # Query for general pool tasks that are unassigned
    query = select(Task).where(
        and_(
            Task.project_id == project_id,
            Task.assignment_type == AssignmentType.GENERAL_POOL,
            Task.assignee_id.is_(None),  # Unassigned
            Task.status.in_([TaskStatus.NOT_STARTED, TaskStatus.BLOCKED])  # Available statuses
        )
    )
    
    if priority:
        query = query.where(Task.priority == priority)
    
    # Order by priority (CRITICAL first) and creation date
    query = query.order_by(
        Task.priority.desc(),  # Assuming CRITICAL > HIGH > MEDIUM > LOW
        Task.created_at.asc()
    )
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # Convert to GeneralPoolTaskOut
    pool_tasks = []
    for task in tasks:
        enriched_task = await _enrich_task_with_user_info(task, db)
        pool_tasks.append(GeneralPoolTaskOut(**enriched_task.model_dump()))
    
    return pool_tasks


async def claim_task(task_id: UUID, db: AsyncSession, current_user_id: UUID) -> TaskOut:
    """
    Claim a task from the general pool.
    
    Args:
        task_id (UUID): The ID of the task to claim.
        db (AsyncSession): The database session.
        current_user_id (UUID): The ID of the user claiming the task.

    Returns:
        TaskOut: The claimed task.
    """
    # Get the task
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permission to claim tasks in this project
    await require_project_permission(
        current_user_id,
        task.project_id,
        ProjectPermission.CLAIM_TASKS,
        db
    )
    
    # Validate task can be claimed
    if task.assignment_type != AssignmentType.GENERAL_POOL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only general pool tasks can be claimed"
        )
    
    if task.assignee_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task is already assigned to someone"
        )
    
    if task.status not in [TaskStatus.NOT_STARTED, TaskStatus.BLOCKED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not available for claiming"
        )
    
    # Claim the task
    task.assignee_id = current_user_id
    task.status = TaskStatus.IN_PROGRESS  # Automatically start when claimed
    
    await db.commit()
    await db.refresh(task)
    
    return await _enrich_task_with_user_info(task, db)


async def update_task(
    task_id: UUID, 
    task_data: TaskUpdate, 
    db: AsyncSession,
    current_user_id: UUID
) -> TaskOut:
    """
    Update an existing task with permission checking.
    
    Args:
        task_id (UUID): The ID of the task to update.
        task_data (TaskUpdate): The new data for the task.
        db (AsyncSession): The database session.
        current_user_id (UUID): The ID of the current user.

    Returns:
        TaskOut: The updated task object.
    """
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Check permissions
    can_edit_any = await user_has_project_permission(
        current_user_id,
        task.project_id,
        ProjectPermission.EDIT_ANY_TASK,
        db
    )
    
    can_edit_own = await user_has_project_permission(
        current_user_id,
        task.project_id,
        ProjectPermission.EDIT_OWN_TASKS,
        db
    )
    
    # User can edit if they can edit any task OR if they can edit own tasks and are assigned
    if not can_edit_any and not (can_edit_own and task.assignee_id == current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this task"
        )

    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    
    # Recalculate project completion if status changed
    if 'status' in update_data:
        await recalculate_project_completion(task.project_id, db)
    
    return await _enrich_task_with_user_info(task, db)


async def delete_task(task_id: UUID, db: AsyncSession, current_user_id: UUID) -> dict:
    """
    Delete a task with permission checking.
    
    Args:
        task_id (UUID): The ID of the task to delete.
        db (AsyncSession): The database session.
        current_user_id (UUID): The ID of the current user.

    Returns:
        dict: Success message.
    """
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permission to delete tasks
    await require_project_permission(
        current_user_id,
        task.project_id,
        ProjectPermission.DELETE_ANY_TASK,
        db
    )
    
    project_id = task.project_id
    
    await db.delete(task)
    await db.commit()
    
    # Recalculate project completion
    await recalculate_project_completion(project_id, db)
    
    return {"message": "Task deleted successfully"}


async def get_user_assigned_tasks(user_id: UUID, db: AsyncSession) -> List[TaskOut]:
    """
    Get all tasks assigned to a specific user across all projects.
    
    Args:
        user_id (UUID): The ID of the user.
        db (AsyncSession): The database session.

    Returns:
        List[TaskOut]: List of tasks assigned to the user.
    """
    query = select(Task).where(Task.assignee_id == user_id)
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # Enrich with user info
    enriched_tasks = []
    for task in tasks:
        enriched_task = await _enrich_task_with_user_info(task, db)
        enriched_tasks.append(enriched_task)
    
    return enriched_tasks



# Helper function to enrich tasks with user's information
async def _enrich_task_with_user_info(task: Task, db: AsyncSession) -> TaskOut:
    """
    Enrich a task with user information (assignee and creator emails).
    
        Args:
            task (Task): The task to enrich.
            db (AsyncSession): The database session.

        Returns:
            TaskOut: The enriched task object.
    """
        
    assignee_email = None
    created_by_email = None

    # Get assignee email if task is assigned
    if task.assignee_id:
        assignee_query = select(User).where(User.id == task.assignee_id)
        assignee_result = await db.execute(assignee_query)
        assignee = assignee_result.scalar_one_or_none()

        if assignee:
            assignee_email = assignee.email

    creator_query = select(User).where(User.id == task.created_by_id)
    creator_result = await db.execute(creator_query)
    creator = creator_result.scalar_one_or_none()

    if creator:
        created_by_email = creator.email


    # Create TaskOut object with all fields
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        project_id=task.project_id,
        assignee_id=task.assignee_id,
        created_by_id=task.created_by_id,
        status=task.status,
        assignment_type=task.assignment_type,
        created_at=task.created_at,
        updated_at=task.updated_at,
        assignee_email=assignee_email,
        created_by_email=created_by_email
    )
