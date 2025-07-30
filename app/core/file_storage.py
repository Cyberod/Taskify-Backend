import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import Tuple


class FileStorage:
    def __init__(self, base_upload_dir: str = "uploads"):
        self.base_upload_dir = Path(base_upload_dir)
        self.base_upload_dir.mkdir(parents=True, exist_ok=True)

    def _get_project_dir(self, project_id: str) -> Path:
        """Get the directory for a specific project"""
        project_dir = self.base_upload_dir / "projects" / str(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir

    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename while preserving the extension"""
        file_extension = Path(original_filename).suffix
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_extension}"

    async def save_file(self, file: UploadFile, project_id: str) -> Tuple[str, str]:
        """
        Save uploaded file and return (stored_filename, file_path)
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        # Validate file size (max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB")

        # Generate unique filename and get project directory
        stored_filename = self._generate_unique_filename(file.filename)
        project_dir = self._get_project_dir(project_id)
        file_path = project_dir / stored_filename

        # Save file
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

        return stored_filename, str(file_path.relative_to(self.base_upload_dir))

    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        try:
            full_path = self.base_upload_dir / file_path
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False

    def get_file_path(self, file_path: str) -> Path:
        """Get the full path to a file"""
        return self.base_upload_dir / file_path

    def validate_file_type(self, filename: str, allowed_extensions: set = None) -> bool:
        """Validate file type based on extension"""
        if allowed_extensions is None:
            # Default allowed extensions
            allowed_extensions = {
                '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
                '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.gif', 
                '.zip', '.rar', '.csv', '.md'
            }
        
        file_extension = Path(filename).suffix.lower()
        return file_extension in allowed_extensions


# Global file storage instance
file_storage = FileStorage()
