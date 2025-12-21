"""
Agent Skills Loader

Reads and parses SKILL.md files following the Agent Skills specification.
Supports YAML frontmatter + Markdown instructions format.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class SkillLoader:
    """Loads and parses Agent Skills from SKILL.md files"""
    
    def __init__(self, skills_dir: str = "backend/ai/skills"):
        """
        Initialize the SkillLoader
        
        Args:
            skills_dir: Base directory containing skill categories
        """
        self.skills_dir = Path(skills_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        if not self.skills_dir.exists():
            raise FileNotFoundError(f"Skills directory not found: {self.skills_dir}")
    
    def load_skill(self, category: str, agent_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load a specific skill by category and agent name
        
        Args:
            category: Category name ('war-room', 'analysis', 'video-production', 'system')
            agent_name: Agent name (e.g., 'trader-agent', 'news-agent')
            use_cache: Whether to use cached version
        
        Returns:
            Dictionary containing:
                - metadata: YAML frontmatter
                - instructions: Markdown content
                - tools: List of allowed tools (if specified)
                - category: Category name
                - agent_name: Agent name
        
        Raises:
            FileNotFoundError: If SKILL.md file doesn't exist
            ValueError: If SKILL.md format is invalid
        """
        cache_key = f"{category}/{agent_name}"
        
        if use_cache and cache_key in self._cache:
            logger.debug(f"Loading skill from cache: {cache_key}")
            return self._cache[cache_key]
        
        skill_path = self.skills_dir / category / agent_name / "SKILL.md"
        
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill file not found: {skill_path}")
        
        logger.info(f"Loading skill: {cache_key}")
        
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML frontmatter
        metadata, instructions = self._parse_skill_file(content)
        
        skill = {
            "metadata": metadata,
            "instructions": instructions,
            "tools": metadata.get("allowed-tools", []),
            "category": category,
            "agent_name": agent_name,
            "skill_path": str(skill_path)
        }
        
        # Validate required metadata
        self._validate_skill(skill)
        
        # Cache the skill
        self._cache[cache_key] = skill
        
        return skill
    
    def _parse_skill_file(self, content: str) -> tuple[Dict[str, Any], str]:
        """
        Parse SKILL.md file into metadata and instructions
        
        Args:
            content: File content
        
        Returns:
            Tuple of (metadata dict, instructions string)
        """
        if not content.startswith('---'):
            raise ValueError("SKILL.md must start with YAML frontmatter (---)")
        
        parts = content.split('---', 2)
        
        if len(parts) < 3:
            raise ValueError("Invalid SKILL.md format: missing closing --- for frontmatter")
        
        try:
            metadata = yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML frontmatter: {e}")
        
        instructions = parts[2].strip()
        
        return metadata, instructions
    
    def _validate_skill(self, skill: Dict[str, Any]) -> None:
        """
        Validate skill has required fields
        
        Args:
            skill: Skill dictionary
        
        Raises:
            ValueError: If required fields are missing
        """
        metadata = skill["metadata"]
        
        required_fields = ["name", "description", "license"]
        missing = [f for f in required_fields if f not in metadata]
        
        if missing:
            raise ValueError(f"Missing required metadata fields: {missing}")
        
        if not skill["instructions"]:
            raise ValueError("Skill instructions cannot be empty")
    
    def get_all_skills(self, category: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Load all skills, optionally filtered by category
        
        Args:
            category: Optional category filter
        
        Returns:
            Dictionary mapping "category/agent-name" to skill data
        """
        skills = {}
        
        if category:
            categories = [category]
        else:
            # All categories
            categories = ['war-room', 'analysis', 'video-production', 'system']
        
        for cat in categories:
            cat_path = self.skills_dir / cat
            
            if not cat_path.exists():
                logger.warning(f"Category directory not found: {cat_path}")
                continue
            
            for skill_dir in cat_path.iterdir():
                if not skill_dir.is_dir():
                    continue
                
                agent_name = skill_dir.name
                skill_md = skill_dir / "SKILL.md"
                
                if not skill_md.exists():
                    logger.warning(f"SKILL.md not found in {skill_dir}")
                    continue
                
                try:
                    skill = self.load_skill(cat, agent_name)
                    skills[f"{cat}/{agent_name}"] = skill
                except Exception as e:
                    logger.error(f"Failed to load {cat}/{agent_name}: {e}")
        
        return skills
    
    def list_categories(self) -> List[str]:
        """List all available skill categories"""
        categories = []
        for item in self.skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                categories.append(item.name)
        return sorted(categories)
    
    def list_agents(self, category: str) -> List[str]:
        """
        List all agents in a category
        
        Args:
            category: Category name
        
        Returns:
            List of agent names
        """
        cat_path = self.skills_dir / category
        
        if not cat_path.exists():
            return []
        
        agents = []
        for item in cat_path.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                agents.append(item.name)
        
        return sorted(agents)
    
    def reload_skill(self, category: str, agent_name: str) -> Dict[str, Any]:
        """
        Force reload a skill (bypass cache)
        
        Args:
            category: Category name
            agent_name: Agent name
        
        Returns:
            Reloaded skill data
        """
        cache_key = f"{category}/{agent_name}"
        if cache_key in self._cache:
            del self._cache[cache_key]
        
        return self.load_skill(category, agent_name, use_cache=False)
    
    def clear_cache(self) -> None:
        """Clear all cached skills"""
        self._cache.clear()
        logger.info("Skill cache cleared")


# Global instance
_skill_loader: Optional[SkillLoader] = None


def get_skill_loader(skills_dir: str = "backend/ai/skills") -> SkillLoader:
    """
    Get or create global SkillLoader instance
    
    Args:
        skills_dir: Skills directory path
    
    Returns:
        SkillLoader instance
    """
    global _skill_loader
    
    if _skill_loader is None:
        _skill_loader = SkillLoader(skills_dir)
    
    return _skill_loader
