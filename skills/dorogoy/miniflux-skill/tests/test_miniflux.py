import os
import subprocess
import pytest


def test_script_exists():
    """Test that miniflux.sh script exists and is executable."""
    script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'miniflux.sh')
    assert os.path.exists(script_path), f"Script not found: {script_path}"
    assert os.access(script_path, os.X_OK), f"Script not executable: {script_path}"


def test_python_cli_exists():
    """Test that miniflux-cli.py exists."""
    cli_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'miniflux-cli.py')
    assert os.path.exists(cli_path), f"Python CLI not found: {cli_path}"


def test_wrapper_script_validates_environment():
    """Test that wrapper script checks for MINIFLUX_TOKEN."""
    script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'miniflux.sh')
    
    with open(script_path, 'r') as f:
        script_content = f.read()
    
    # Check that script validates environment
    assert 'MINIFLUX_TOKEN' in script_content, "Script should validate MINIFLUX_TOKEN"
    assert 'MINIFLUX_URL' in script_content, "Script should set MINIFLUX_URL"


def test_wrapper_calls_python_cli():
    """Test that wrapper script calls Python CLI."""
    script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'miniflux.sh')
    
    with open(script_path, 'r') as f:
        script_content = f.read()
    
    # Check that it calls Python script
    assert 'python3' in script_content, "Wrapper should call python3"
    assert 'miniflux-cli.py' in script_content, "Wrapper should call miniflux-cli.py"


def test_skill_documentation_exists():
    """Test that SKILL.md and README.md exist."""
    base_dir = os.path.dirname(__file__)
    
    assert os.path.exists(os.path.join(base_dir, '..', 'SKILL.md')), "SKILL.md not found"
    assert os.path.exists(os.path.join(base_dir, '..', 'README.md')), "README.md not found"


def test_skill_documentation_has_required_sections():
    """Test that SKILL.md has required sections."""
    skill_md_path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
    
    with open(skill_md_path, 'r') as f:
        content = f.read()
    
    required_sections = [
        '## Setup',
        '## Configuration',
        '## Usage',
        '## Commands Reference'
    ]
    
    for section in required_sections:
        assert section in content, f"Missing section in SKILL.md: {section}"


def test_readme_exists_and_has_content():
    """Test that README.md has content."""
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    assert len(content) > 100, "README.md is too short"
    assert '# Miniflux Skill for OpenClaw' in content, "README.md should have title"


def test_python_cli_imports_miniflux():
    """Test that Python CLI imports miniflux package."""
    cli_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'miniflux-cli.py')
    
    with open(cli_path, 'r') as f:
        cli_content = f.read()
    
    assert 'import miniflux' in cli_content, "Python CLI should import miniflux package"


def test_python_cli_has_api_functions():
    """Test that Python CLI has API functions."""
    cli_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'miniflux-cli.py')
    
    with open(cli_path, 'r') as f:
        cli_content = f.read()
    
    # Check for key API calls
    required_api_calls = ['get_entries', 'get_feeds', 'create_feed']
    for api_call in required_api_calls:
        assert api_call in cli_content, f"Missing API call: {api_call}"
