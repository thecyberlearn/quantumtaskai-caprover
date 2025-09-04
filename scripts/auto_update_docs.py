#!/usr/bin/env python3
"""
Auto Documentation Update Script
Automatically updates README.md, CLAUDE.md, and docs/ files based on recent changes
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set

class DocumentationUpdater:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.changes_summary = {}
        self.updated_files = []
        
    def analyze_recent_changes(self, commit_count: int = 5) -> Dict:
        """Analyze recent git commits to understand what changed"""
        try:
            # Get recent commit messages
            result = subprocess.run([
                'git', 'log', f'--oneline', f'-{commit_count}'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            commits = result.stdout.strip().split('\n') if result.stdout else []
            
            # Get changed files in recent commits
            result = subprocess.run([
                'git', 'diff', 'HEAD~1', '--name-only'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            changed_files = result.stdout.strip().split('\n') if result.stdout else []
            
            # Categorize changes
            categories = {
                'agents': [],
                'core': [],
                'deployment': [],
                'documentation': [],
                'frontend': [],
                'backend': []
            }
            
            for file in changed_files:
                if not file:
                    continue
                    
                file_lower = file.lower()
                if any(agent in file for agent in ['agent', 'processor', 'models.py']):
                    categories['agents'].append(file)
                elif any(core in file for core in ['settings', 'urls.py', 'views.py']):
                    categories['core'].append(file)
                elif any(deploy in file for deploy in ['railway', 'requirements', 'docker']):
                    categories['deployment'].append(file)
                elif file_lower.endswith('.md') or 'docs/' in file:
                    categories['documentation'].append(file)
                elif any(frontend in file for frontend in ['.html', '.css', '.js']):
                    categories['frontend'].append(file)
                else:
                    categories['backend'].append(file)
            
            return {
                'commits': commits,
                'changed_files': changed_files,
                'categories': categories,
                'analysis_date': datetime.now().isoformat()
            }
            
        except subprocess.CalledProcessError as e:
            print(f"Error analyzing git changes: {e}")
            return {}
    
    def find_documentation_files(self) -> Dict[str, List[Path]]:
        """Find all documentation files in the project"""
        doc_files = {
            'readme': [],
            'claude_md': [],
            'docs_directory': []
        }
        
        # Find README files
        for readme in self.project_root.rglob('README.md'):
            doc_files['readme'].append(readme)
        
        # Find CLAUDE.md files
        for claude in self.project_root.rglob('CLAUDE.md'):
            doc_files['claude_md'].append(claude)
        
        # Find docs directory files
        docs_path = self.project_root / 'docs'
        if docs_path.exists():
            for doc_file in docs_path.rglob('*.md'):
                doc_files['docs_directory'].append(doc_file)
        
        return doc_files
    
    def should_update_documentation(self, changes: Dict) -> bool:
        """Determine if documentation updates are needed"""
        # Check if significant changes were made
        categories = changes.get('categories', {})
        
        # Always update if agents, core, or deployment changed
        significant_changes = (
            categories.get('agents', []) or
            categories.get('core', []) or
            categories.get('deployment', [])
        )
        
        # Check commit messages for documentation keywords
        commits = changes.get('commits', [])
        doc_keywords = ['add', 'update', 'new', 'feature', 'agent', 'deploy']
        
        has_doc_worthy_commits = any(
            any(keyword in commit.lower() for keyword in doc_keywords)
            for commit in commits
        )
        
        return bool(significant_changes or has_doc_worthy_commits)
    
    def update_claude_md(self, changes: Dict) -> bool:
        """Update CLAUDE.md with recent changes"""
        claude_file = self.project_root / 'CLAUDE.md'
        if not claude_file.exists():
            return False
        
        try:
            content = claude_file.read_text()
            original_content = content
            updated = False
            
            categories = changes.get('categories', {})
            
            # Update project overview if agents were added/modified
            if categories.get('agents'):
                # This is a simplified example - in practice, you'd parse and update specific sections
                overview_pattern = r'(## Project Overview.*?)(## Development Commands)'
                if re.search(overview_pattern, content, re.DOTALL):
                    print("Found project overview section in CLAUDE.md")
                    # Add logic to update agent count, new agent descriptions, etc.
                    updated = True
            
            # Update commands section if new scripts were added
            if any('manage.py' in f or 'script' in f for f in changes.get('changed_files', [])):
                print("Detected management command changes")
                updated = True
            
            # Update environment variables section if settings changed
            if any('settings' in f or 'env' in f for f in changes.get('changed_files', [])):
                print("Detected environment/settings changes")
                updated = True
            
            # Add timestamp of last update
            if updated:
                timestamp_pattern = r'(Last updated: )[\d\-:T\s]+\n'
                new_timestamp = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                
                if re.search(timestamp_pattern, content):
                    content = re.sub(timestamp_pattern, f"\\1{new_timestamp}", content)
                else:
                    # Add timestamp at the end
                    content += f"\n\n---\nLast updated: {new_timestamp}"
                
                claude_file.write_text(content)
                self.updated_files.append(str(claude_file))
                return True
            
            return updated
            
        except Exception as e:
            print(f"Error updating CLAUDE.md: {e}")
            return False
    
    def update_readme(self, changes: Dict) -> bool:
        """Update README.md with recent changes"""
        readme_file = self.project_root / 'README.md'
        if not readme_file.exists():
            return False
        
        try:
            content = readme_file.read_text()
            updated = False
            
            categories = changes.get('categories', {})
            
            # Update features section if new agents were added
            if categories.get('agents'):
                print("Updating README features section for new agents")
                updated = True
            
            # Update installation section if requirements changed
            if any('requirements' in f or 'setup' in f for f in changes.get('changed_files', [])):
                print("Updating README installation section")
                updated = True
            
            if updated:
                readme_file.write_text(content)
                self.updated_files.append(str(readme_file))
                return True
            
            return False
            
        except Exception as e:
            print(f"Error updating README.md: {e}")
            return False
    
    def update_docs_directory(self, changes: Dict) -> bool:
        """Update files in docs/ directory"""
        docs_path = self.project_root / 'docs'
        if not docs_path.exists():
            return False
        
        updated_any = False
        categories = changes.get('categories', {})
        
        # Update agent creation guide if agent changes were made
        if categories.get('agents'):
            agent_guide = docs_path / 'development' / 'agent-creation.md'
            if agent_guide.exists():
                print("Updating agent creation guide")
                # Add new patterns, update examples, etc.
                updated_any = True
                self.updated_files.append(str(agent_guide))
        
        # Update deployment guide if deployment files changed
        if categories.get('deployment'):
            deploy_guide = docs_path / 'deployment' / 'railway-deployment.md'
            if deploy_guide.exists():
                print("Updating deployment guide")
                updated_any = True
                self.updated_files.append(str(deploy_guide))
        
        return updated_any
    
    def generate_update_summary(self, changes: Dict) -> str:
        """Generate a summary of what was updated"""
        summary = []
        summary.append("=== Documentation Auto-Update Summary ===")
        summary.append(f"Update Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        # Recent commits
        commits = changes.get('commits', [])
        if commits:
            summary.append("Recent Commits:")
            for commit in commits[:3]:  # Show last 3 commits
                summary.append(f"  - {commit}")
            summary.append("")
        
        # Changed files by category
        categories = changes.get('categories', {})
        for category, files in categories.items():
            if files:
                summary.append(f"{category.title()} Changes:")
                for file in files[:5]:  # Show up to 5 files per category
                    summary.append(f"  - {file}")
                summary.append("")
        
        # Updated documentation files
        if self.updated_files:
            summary.append("Updated Documentation Files:")
            for file in self.updated_files:
                summary.append(f"  - {file}")
        else:
            summary.append("No documentation files required updates.")
        
        summary.append("")
        summary.append("=== End Summary ===")
        
        return "\n".join(summary)
    
    def run_update(self) -> str:
        """Main method to run the documentation update process"""
        print("Starting documentation auto-update...")
        
        # Analyze recent changes
        changes = self.analyze_recent_changes()
        
        if not changes:
            return "Error: Could not analyze recent changes"
        
        # Check if updates are needed
        if not self.should_update_documentation(changes):
            return "No significant changes detected - documentation update skipped"
        
        # Find documentation files
        doc_files = self.find_documentation_files()
        print(f"Found documentation files: {sum(len(files) for files in doc_files.values())}")
        
        # Update each type of documentation
        updated_claude = self.update_claude_md(changes)
        updated_readme = self.update_readme(changes)
        updated_docs = self.update_docs_directory(changes)
        
        # Generate and save summary
        summary = self.generate_update_summary(changes)
        
        # Save summary to file
        summary_file = self.project_root / 'docs_update_summary.txt'
        summary_file.write_text(summary)
        
        print(summary)
        return summary

def main():
    """Main entry point"""
    project_root = sys.argv[1] if len(sys.argv) > 1 else None
    
    updater = DocumentationUpdater(project_root)
    result = updater.run_update()
    
    return result

if __name__ == "__main__":
    main()