"""Tests for README.md documentation validation.

This module validates the README.md file for:
- Required sections and structure
- Link and URL format
- Code block syntax
- Badge format
- Content accuracy
- Markdown formatting
"""

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pytest


@pytest.fixture
def readme_path() -> Path:
    """Return the path to the README.md file.

    Returns:
        Path: Path object pointing to README.md in the repository root.
    """
    return Path(__file__).parent.parent / "README.md"


@pytest.fixture
def readme_content(readme_path: Path) -> str:
    """Read and return the content of README.md.

    Args:
        readme_path (Path): Path to the README.md file.

    Returns:
        str: The full content of README.md.
    """
    return readme_path.read_text(encoding="utf-8")


@pytest.fixture
def readme_lines(readme_content: str) -> list[str]:
    """Return README content as a list of lines.

    Args:
        readme_content (str): The full content of README.md.

    Returns:
        list[str]: List of lines from README.md.
    """
    return readme_content.split("\n")


class TestReadmeStructure:
    """Test suite for README.md structural validation."""

    def test_readme_exists(self, readme_path: Path) -> None:
        """Test that README.md file exists in the repository root.

        Args:
            readme_path (Path): Path to the README.md file.
        """
        assert readme_path.exists(), "README.md file must exist in repository root"
        assert readme_path.is_file(), "README.md must be a file, not a directory"

    def test_readme_not_empty(self, readme_content: str) -> None:
        """Test that README.md is not empty.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert len(readme_content.strip()) > 0, "README.md must not be empty"
        assert len(readme_content) > 100, "README.md should contain substantial content"

    def test_required_sections_exist(self, readme_content: str) -> None:
        """Test that all required sections exist in README.md.

        Args:
            readme_content (str): The full content of README.md.
        """
        required_sections = [
            "# Mixemy",
            "## Features",
            "## Installation",
            "## Getting Started",
            "## License",
            "## Contributing",
        ]

        for section in required_sections:
            assert (
                section in readme_content
            ), f"Required section '{section}' must be present in README.md"

    def test_header_hierarchy(self, readme_lines: list[str]) -> None:
        """Test that headers follow proper Markdown hierarchy.

        Args:
            readme_lines (list[str]): List of lines from README.md.
        """
        header_pattern = re.compile(r"^(#{1,6})\s+(.+)$")
        previous_level = 0

        for line in readme_lines:
            match = header_pattern.match(line)
            if match:
                current_level = len(match.group(1))
                # H1 should only appear once at the top
                if current_level == 1:
                    assert (
                        previous_level == 0
                    ), "Only one H1 header should exist at the start"
                # Headers shouldn't skip levels (e.g., H2 -> H4)
                if previous_level > 0:
                    assert (
                        current_level <= previous_level + 1
                    ), f"Header level jumped from H{previous_level} to H{current_level}"
                previous_level = current_level

    def test_no_trailing_whitespace(self, readme_lines: list[str]) -> None:
        """Test that lines do not have trailing whitespace.

        Args:
            readme_lines (list[str]): List of lines from README.md.
        """
        lines_with_trailing = [
            i + 1 for i, line in enumerate(readme_lines) if line.endswith((" ", "\t"))
        ]

        assert (
            len(lines_with_trailing) == 0
        ), f"Lines with trailing whitespace: {lines_with_trailing}"


class TestReadmeCodeBlocks:
    """Test suite for code block validation in README.md."""

    def test_code_blocks_balanced(self, readme_content: str) -> None:
        """Test that code block markers (```) are properly balanced.

        Args:
            readme_content (str): The full content of README.md.
        """
        code_fence_count = readme_content.count("```")
        assert (
            code_fence_count % 2 == 0
        ), f"Code block fences must be balanced (found {code_fence_count})"

    def test_code_blocks_have_language(self, readme_lines: list[str]) -> None:
        """Test that code blocks specify a language.

        Args:
            readme_lines (list[str]): List of lines from README.md.
        """
        code_block_pattern = re.compile(r"^```(\w+)?$")
        in_code_block = False
        issues = []

        for i, line in enumerate(readme_lines):
            if line.startswith("```"):
                if not in_code_block:
                    # Opening fence
                    match = code_block_pattern.match(line)
                    if match and not match.group(1):
                        issues.append(i + 1)
                    in_code_block = True
                else:
                    # Closing fence
                    in_code_block = False

        assert (
            len(issues) == 0
        ), f"Code blocks without language specification at lines: {issues}"

    def test_bash_code_blocks_valid(self, readme_content: str) -> None:
        """Test that bash code blocks contain valid commands.

        Args:
            readme_content (str): The full content of README.md.
        """
        bash_pattern = re.compile(r"```bash\n(.*?)```", re.DOTALL)
        bash_blocks = bash_pattern.findall(readme_content)

        for block in bash_blocks:
            # Should not be empty
            assert block.strip(), "Bash code blocks should not be empty"
            # Should not contain obvious errors
            assert (
                "command not found" not in block.lower()
            ), "Bash blocks should not contain error messages"

    def test_python_code_blocks_valid_syntax(self, readme_content: str) -> None:
        """Test that Python code blocks have valid basic syntax.

        Args:
            readme_content (str): The full content of README.md.
        """
        python_pattern = re.compile(r"```python\n(.*?)```", re.DOTALL)
        python_blocks = python_pattern.findall(readme_content)

        assert len(python_blocks) > 0, "README should contain Python code examples"

        for block in python_blocks:
            # Should not be empty
            assert block.strip(), "Python code blocks should not be empty"
            # Check for balanced parentheses and brackets
            assert block.count("(") == block.count(
                ")"
            ), "Python code should have balanced parentheses"
            assert block.count("[") == block.count(
                "]"
            ), "Python code should have balanced brackets"
            # Should contain typical Python patterns
            assert any(
                keyword in block
                for keyword in ["import", "class", "def", "async", "=", "from"]
            ), "Python blocks should contain recognizable Python syntax"


class TestReadmeLinks:
    """Test suite for link validation in README.md."""

    def test_all_links_have_valid_format(self, readme_content: str) -> None:
        """Test that all Markdown links have valid format.

        Args:
            readme_content (str): The full content of README.md.
        """
        # Match markdown links: [text](url)
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
        links = link_pattern.findall(readme_content)

        assert len(links) > 0, "README should contain links"

        for text, url in links:
            assert text.strip(), f"Link text should not be empty for URL: {url}"
            assert url.strip(), f"Link URL should not be empty for text: {text}"
            assert not url.startswith(" "), f"URL should not start with space: {url}"
            assert not url.endswith(" "), f"URL should not end with space: {url}"

    def test_external_urls_valid_format(self, readme_content: str) -> None:
        """Test that external URLs have valid format.

        Args:
            readme_content (str): The full content of README.md.
        """
        # Extract all URLs
        url_pattern = re.compile(r"https?://[^\s\)]+")
        urls = url_pattern.findall(readme_content)

        assert len(urls) > 0, "README should contain external URLs"

        for url in urls:
            parsed = urlparse(url)
            assert parsed.scheme in [
                "http",
                "https",
            ], f"URL should use http or https: {url}"
            assert parsed.netloc, f"URL should have a valid domain: {url}"

    def test_github_urls_correct(self, readme_content: str) -> None:
        """Test that GitHub URLs point to the correct repository.

        Args:
            readme_content (str): The full content of README.md.
        """
        github_pattern = re.compile(r"https://github\.com/([^/\s\)]+)/([^/\s\)]+)")
        github_urls = github_pattern.findall(readme_content)

        assert len(github_urls) > 0, "README should contain GitHub URLs"

        for owner, repo in github_urls:
            # Check expected repository
            if owner == "frostyfeet909":
                assert (
                    repo == "mixemy"
                ), f"GitHub URLs should point to frostyfeet909/mixemy, found {owner}/{repo}"

    def test_badge_links_valid(self, readme_content: str) -> None:
        """Test that badge image links have valid format.

        Args:
            readme_content (str): The full content of README.md.
        """
        # Match badge format: [![text](image_url)](link_url)
        badge_pattern = re.compile(r"!\[([^\]]*)\]\(([^\)]+)\)")
        badges = badge_pattern.findall(readme_content)

        assert len(badges) > 0, "README should contain badges"

        for alt_text, image_url in badges:
            assert (
                image_url.strip()
            ), f"Badge image URL should not be empty: {alt_text}"
            # Badge images should be from trusted sources
            assert any(
                domain in image_url
                for domain in [
                    "github.com",
                    "shields.io",
                    "microsoft.github.io",
                    "img.shields.io",
                    "raw.githubusercontent.com",
                    "./badges/",
                ]
            ), f"Badge should be from a trusted source: {image_url}"

    def test_relative_links_valid(self, readme_content: str) -> None:
        """Test that relative links in the repository are valid.

        Args:
            readme_content (str): The full content of README.md.
        """
        # Match links that are relative (not starting with http/https)
        relative_link_pattern = re.compile(r"\[([^\]]+)\]\(([^h][^\)]+)\)")
        relative_links = relative_link_pattern.findall(readme_content)

        for _text, url in relative_links:
            # Relative links should not contain spaces
            assert " " not in url.strip(), f"Relative URL should not contain spaces: {url}"
            # Should be reasonable paths
            assert not url.startswith(
                "//"
            ), f"Relative URL should not start with '//': {url}"


class TestReadmeContent:
    """Test suite for README.md content validation."""

    def test_project_name_consistency(self, readme_content: str) -> None:
        """Test that project name 'Mixemy' is used consistently.

        Args:
            readme_content (str): The full content of README.md.
        """
        # Should contain the project name multiple times
        assert (
            readme_content.count("Mixemy") >= 5
        ), "Project name 'Mixemy' should appear multiple times"
        assert (
            readme_content.count("mixemy") >= 5
        ), "Package name 'mixemy' should appear multiple times"

    def test_installation_instructions_present(self, readme_content: str) -> None:
        """Test that installation instructions are present.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert (
            "pip install mixemy" in readme_content
        ), "Installation instructions should include 'pip install mixemy'"

    def test_usage_examples_present(self, readme_content: str) -> None:
        """Test that usage examples are present in README.

        Args:
            readme_content (str): The full content of README.md.
        """
        # Should contain imports from the package
        assert "from mixemy import" in readme_content, "Should contain import examples"
        assert (
            "repositories" in readme_content
        ), "Should mention repositories module"
        assert "services" in readme_content, "Should mention services module"
        assert "schemas" in readme_content, "Should mention schemas module"

    def test_async_and_sync_examples(self, readme_content: str) -> None:
        """Test that both async and sync examples are present.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert (
            "async def" in readme_content
        ), "Should contain async function examples"
        assert (
            "def main" in readme_content or "def " in readme_content
        ), "Should contain sync function examples"
        assert (
            "AsyncSession" in readme_content
        ), "Should mention AsyncSession for async operations"
        assert "Session" in readme_content, "Should mention Session for sync operations"

    def test_license_mentioned(self, readme_content: str) -> None:
        """Test that license information is mentioned.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert "MIT License" in readme_content, "License type should be specified"
        assert "LICENSE" in readme_content, "Should reference LICENSE file"

    def test_contributing_guidelines(self, readme_content: str) -> None:
        """Test that contributing guidelines are present.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert (
            "Contributing" in readme_content or "Contributions" in readme_content
        ), "Should have contributing section"
        assert (
            "pull request" in readme_content.lower()
        ), "Should mention pull requests"


class TestReadmeCICD:
    """Test suite for CI/CD section in README.md."""

    def test_cicd_section_exists(self, readme_content: str) -> None:
        """Test that CI/CD section exists.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert "CI/CD" in readme_content, "README should have CI/CD section"
        assert (
            "### CI/CD" in readme_content
        ), "CI/CD should be a subsection under Contributing"

    def test_github_actions_mentioned(self, readme_content: str) -> None:
        """Test that GitHub Actions is mentioned in CI/CD section.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert (
            "GitHub Actions" in readme_content
        ), "CI/CD section should mention GitHub Actions"
        assert (
            "continuous integration" in readme_content
        ), "Should mention continuous integration"
        assert (
            "continuous deployment" in readme_content
        ), "Should mention continuous deployment"

    def test_ci_workflow_description(self, readme_content: str) -> None:
        """Test that CI workflow is properly described.

        Args:
            readme_content (str): The full content of README.md.
        """
        ci_keywords = ["tests", "linters", "type checkers"]

        for keyword in ci_keywords:
            assert (
                keyword in readme_content
            ), f"CI/CD section should mention {keyword}"

    def test_coderabbit_mentioned(self, readme_content: str) -> None:
        """Test that CodeRabbit is mentioned in CI/CD section.

        This validates the new content added to the README.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert (
            "CodeRabbit" in readme_content
        ), "CI/CD section should mention CodeRabbit"
        assert (
            "code quality analysis" in readme_content.lower()
            or "code quality" in readme_content.lower()
        ), "Should mention code quality analysis"

    def test_local_ci_instructions(self, readme_content: str) -> None:
        """Test that local CI execution instructions are present.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert (
            "poetry run" in readme_content
        ), "Should include poetry commands for local execution"
        assert (
            "pre-commit" in readme_content
        ), "Should mention pre-commit for local validation"


class TestReadmeBadges:
    """Test suite for badge validation in README.md."""

    def test_ci_badge_present(self, readme_content: str) -> None:
        """Test that CI badge is present.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert "![CI]" in readme_content or "[![CI]" in readme_content, "Should have CI badge"
        assert (
            "workflows/ci.yml" in readme_content
        ), "CI badge should link to ci.yml workflow"

    def test_cd_badge_present(self, readme_content: str) -> None:
        """Test that CD badge is present.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert "![CD]" in readme_content or "[![CD]" in readme_content, "Should have CD badge"
        assert (
            "workflows/cd.yml" in readme_content
        ), "CD badge should link to cd.yml workflow"

    def test_quality_badges_present(self, readme_content: str) -> None:
        """Test that code quality badges are present.

        Args:
            readme_content (str): The full content of README.md.
        """
        quality_tools = ["Ruff", "pyright", "Poetry"]

        for tool in quality_tools:
            assert (
                tool in readme_content
            ), f"Should have badge or mention for {tool}"

    def test_test_coverage_badges(self, readme_content: str) -> None:
        """Test that test and coverage badges are present.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert (
            "![Tests]" in readme_content or "Tests" in readme_content
        ), "Should have tests badge"
        assert (
            "![Coverage]" in readme_content or "Coverage" in readme_content
        ), "Should have coverage badge"


class TestReadmeFormatting:
    """Test suite for README.md formatting and style."""

    def test_proper_emphasis(self, readme_content: str) -> None:
        """Test that emphasis markers are properly balanced.

        Args:
            readme_content (str): The full content of README.md.
        """
        # Count bold markers
        bold_count = readme_content.count("**")
        assert (
            bold_count % 2 == 0
        ), f"Bold markers (**) should be balanced (found {bold_count})"

        # Count italic markers (excluding asterisks in lists)
        lines_without_lists = [
            line for line in readme_content.split("\n") if not line.strip().startswith("*")
        ]
        content_without_lists = "\n".join(lines_without_lists)
        # Remove bold markers to count italics
        content_for_italics = content_without_lists.replace("**", "")
        italic_count = content_for_italics.count("*")
        assert (
            italic_count % 2 == 0
        ), f"Italic markers (*) should be balanced (found {italic_count})"

    def test_list_formatting(self, readme_lines: list[str]) -> None:
        """Test that lists are properly formatted.

        Args:
            readme_lines (list[str]): List of lines from README.md.
        """
        list_pattern = re.compile(r"^(\s*)([-*+]|\d+\.)\s+(.+)$")
        in_list = False
        previous_indent = 0

        for line in readme_lines:
            match = list_pattern.match(line)
            if match:
                indent = len(match.group(1))
                # Indentation should be consistent (multiples of 2 or 4)
                if in_list and indent > previous_indent:
                    assert indent - previous_indent in [
                        2,
                        4,
                    ], f"List indentation should increase by 2 or 4 spaces: '{line}'"
                in_list = True
                previous_indent = indent
            elif line.strip() == "":
                in_list = False
                previous_indent = 0

    def test_no_multiple_blank_lines(self, readme_lines: list[str]) -> None:
        """Test that there are no multiple consecutive blank lines.

        Args:
            readme_lines (list[str]): List of lines from README.md.
        """
        consecutive_blanks = 0
        max_consecutive = 0

        for line in readme_lines:
            if not line.strip():
                consecutive_blanks += 1
                max_consecutive = max(max_consecutive, consecutive_blanks)
            else:
                consecutive_blanks = 0

        assert (
            max_consecutive <= 2
        ), f"Should not have more than 2 consecutive blank lines (found {max_consecutive})"

    def test_section_spacing(self, readme_lines: list[str]) -> None:
        """Test that sections have proper spacing.

        Args:
            readme_lines (list[str]): List of lines from README.md.
        """
        header_pattern = re.compile(r"^##\s+.+$")

        for i, line in enumerate(readme_lines[:-1]):
            if header_pattern.match(line):
                # There should be a blank line before headers (except after another header or at start)
                if i > 0 and readme_lines[i - 1].strip():
                    previous_is_header = readme_lines[i - 1].startswith("#")
                    assert previous_is_header or not readme_lines[i - 1].strip(), (
                        f"Section header at line {i + 1} should have blank line before it: "
                        f"'{line}'"
                    )


class TestReadmeCompleteness:
    """Test suite for README.md completeness."""

    def test_key_features_documented(self, readme_content: str) -> None:
        """Test that key features are documented.

        Args:
            readme_content (str): The full content of README.md.
        """
        key_features = [
            "CRUD",
            "async",
            "sync",
            "repository",
            "service",
            "schema",
            "Pydantic",
            "SQLAlchemy",
        ]

        for feature in key_features:
            assert (
                feature.lower() in readme_content.lower()
            ), f"Key feature '{feature}' should be documented"

    def test_prerequisites_mentioned(self, readme_content: str) -> None:
        """Test that prerequisites or dependencies are mentioned.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert (
            "pip install" in readme_content or "poetry" in readme_content
        ), "Installation method should be documented"

    def test_examples_are_complete(self, readme_content: str) -> None:
        """Test that code examples are complete and runnable.

        Args:
            readme_content (str): The full content of README.md.
        """
        # Examples should show imports
        assert "import" in readme_content, "Examples should include imports"
        # Examples should show class definitions
        assert (
            "class " in readme_content
        ), "Examples should include class definitions"
        # Examples should show actual usage
        assert (
            "= " in readme_content or "await " in readme_content
        ), "Examples should show actual usage patterns"

    def test_contact_or_support_info(self, readme_content: str) -> None:
        """Test that contact or support information is available.

        Args:
            readme_content (str): The full content of README.md.
        """
        assert (
            "github.com" in readme_content.lower()
        ), "Should provide GitHub link for support"
        assert (
            "issue" in readme_content.lower()
        ), "Should mention issues for support"


# Integration test that validates the entire README as a cohesive document
@pytest.mark.integration
def test_readme_overall_quality(readme_content: str) -> None:
    """Integration test for overall README.md quality.

    This test validates that the README is comprehensive, well-structured,
    and provides value to users.

    Args:
        readme_content (str): The full content of README.md.
    """
    # Should be substantial
    assert (
        len(readme_content) > 5000
    ), "README should be comprehensive (>5000 characters)"

    # Should have multiple sections
    section_count = readme_content.count("## ")
    assert section_count >= 8, f"README should have at least 8 main sections (found {section_count})"

    # Should have code examples
    code_block_count = readme_content.count("```")
    assert (
        code_block_count >= 10
    ), f"README should have multiple code examples (found {code_block_count // 2} blocks)"

    # Should have external links
    link_count = readme_content.count("http")
    assert link_count >= 10, f"README should have external references (found {link_count})"

    # Should mention the new CI/CD enhancement (CodeRabbit)
    assert (
        "CodeRabbit" in readme_content
    ), "README should mention CodeRabbit for code quality"