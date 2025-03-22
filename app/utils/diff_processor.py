from typing import List, Dict, Any, Optional, Tuple
import re
from app.models.gitlab import Change
from app.models.config import CodeReviewConfig

class DiffProcessor:
    """Process Git diffs for code review"""
    
    def __init__(self, config: CodeReviewConfig):
        self.config = config
        
    def should_review_file(self, file_path: str) -> bool:
        """Check if a file should be reviewed based on config"""
        # Skip files in excluded paths
        for excluded in self.config.excluded_paths:
            if excluded in file_path:
                return False
        
        # Check if file extension is in the list of reviewed extensions
        for ext in self.config.file_extensions:
            if file_path.endswith(ext):
                return True
                
        return False
        
    def filter_changes(self, changes: List[Change]) -> List[Change]:
        """Filter changes based on configuration rules"""
        filtered = []
        
        for change in changes:
            if change.deleted_file:
                continue  # Skip deleted files
                
            if not self.should_review_file(change.new_path):
                continue  # Skip files that don't match our criteria
                
            # Check file size limitations
            if self._count_diff_lines(change.diff) > self.config.max_lines_per_file:
                # TODO: Consider chunking large files instead of skipping
                continue
                
            filtered.append(change)
            
            # Limit the number of files
            if len(filtered) >= self.config.max_files_per_review:
                break
                
        return filtered
    
    def _count_diff_lines(self, diff: str) -> int:
        """Count the number of lines in a diff"""
        # Skip diff header lines
        content_lines = 0
        for line in diff.split('\n'):
            if line.startswith('+') or line.startswith('-'):
                content_lines += 1
        return content_lines
    
    def extract_diff_chunks(self, diff: str) -> List[Dict[str, Any]]:
        """Extract code chunks from a diff for focused review"""
        chunks = []
        current_chunk = None
        lines = diff.split('\n')
        
        for line in lines:
            # New chunk header
            if line.startswith('@@'):
                if current_chunk:
                    chunks.append(current_chunk)
                
                # Parse the header, e.g. @@ -1,7 +1,9 @@
                match = re.search(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
                if match:
                    old_start = int(match.group(1))
                    old_count = int(match.group(2)) if match.group(2) else 1
                    new_start = int(match.group(3))
                    new_count = int(match.group(4)) if match.group(4) else 1
                    
                    current_chunk = {
                        'header': line,
                        'old_start': old_start,
                        'old_count': old_count,
                        'new_start': new_start,
                        'new_count': new_count,
                        'lines': [line],
                        'context_before': [],
                        'context_after': []
                    }
            elif current_chunk is not None:
                current_chunk['lines'].append(line)
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    def get_line_mapping(self, diff: str) -> Dict[int, int]:
        """Map diff lines to actual file lines"""
        mapping = {}
        line_num = 0
        file_line = 0
        
        for line in diff.split('\n'):
            line_num += 1
            
            if not line.startswith('-'):  # Skip deleted lines for mapping
                file_line += 1
                mapping[line_num] = file_line
                
        return mapping
    
    def chunk_large_diff(self, diff: str, max_lines: int = 500) -> List[str]:
        """Split large diffs into manageable chunks"""
        chunks = []
        lines = diff.split('\n')
        
        # Process in chunks
        for i in range(0, len(lines), max_lines):
            chunk = '\n'.join(lines[i:i+max_lines])
            chunks.append(chunk)
            
        return chunks