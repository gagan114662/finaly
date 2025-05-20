import logging
import re
import ast

logger = logging.getLogger(__name__)

class CodeGeneratorAgent:
    def __init__(self):
        logger.info("CodeGeneratorAgent initialized")

    async def generate_code(self,
                          prompt: str,
                          parent_code: str = None,
                          temperature: float = 0.7,
                          syntax_validation: bool = True,
                          max_length: int = 2000,
                          output_format: str = "python") -> str:
        """
        Generates new code based on the given prompt and optional parent code.
        Args:
            prompt: The prompt describing the code to generate
            parent_code: Optional existing code to modify
            temperature: Creativity parameter (0.0-1.0)
            syntax_validation: Whether to validate syntax of generated code
            max_length: Maximum length of generated code
            output_format: Format of generated code (e.g. "python", "diff")
        Returns:
            The generated code as a string
        """
        logger.info(f"Generating code from prompt: {prompt[:100]}... (temperature={temperature}, syntax_validation={syntax_validation}, max_length={max_length})")
        
        # Generate initial code
        generated_code = await self._call_llm(prompt, parent_code, temperature, max_length)
        
        if syntax_validation:
            try:
                # Validate syntax by compiling
                ast.parse(generated_code)
            except SyntaxError as e:
                logger.warning(f"Syntax error in generated code: {e}")
                # Attempt to fix common indentation errors
                generated_code = self._fix_indentation(generated_code)
                try:
                    ast.parse(generated_code)  # Validate again after fix
                except SyntaxError:
                    logger.error("Failed to fix syntax errors in generated code")
                    raise
                    
        return generated_code

    async def _call_llm(self, prompt: str, parent_code: str, temperature: float, max_length: int) -> str:
        """Call the LLM to generate code with proper structure"""
        # Example implementation - in production this would call an actual LLM API
        example_code = '''def example_function():
    """Example docstring"""
    for i in range(10):
        if i % 2 == 0:
            print(f"Even: {i}")
        else:
            print(f"Odd: {i}")
    return True'''
        
        return example_code

    def _fix_indentation(self, code: str) -> str:
        """Fix indentation issues in generated code"""
        lines = code.splitlines()
        fixed_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Handle block closers first
            if stripped.startswith(('return ', 'break ', 'continue ', 'pass ')):
                fixed_lines.append('    ' * indent_level + stripped)
                continue
                
            # Handle block starters
            if stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except ', 'finally:')):
                fixed_lines.append('    ' * indent_level + stripped)
                indent_level += 1
                continue
                
            # Handle block enders
            if stripped in ('else:', 'elif ', 'except:', 'finally:'):
                indent_level -= 1
                fixed_lines.append('    ' * indent_level + stripped)
                indent_level += 1
                continue
                
            # Handle regular lines
            if stripped:
                fixed_lines.append('    ' * indent_level + stripped)
            else:
                fixed_lines.append('')
                
        return '\n'.join(fixed_lines)
        
        if parent_code:
            # If parent code provided, generate a diff
            async def _generate_diff(self, prompt: str, parent_code: str) -> str:
                """Generate a diff between parent code and new version"""
                # Implementation would go here
                return "# Generated diff placeholder"
            return self._apply_diff(parent_code, diff_text)
        else:
            # Generate completely new code
            async def _generate_new_code(self, prompt: str) -> str:
                """Generate new code from prompt"""
                # Implementation would go here
                return "# Generated new code placeholder"

    async def _generate_diff(self, prompt: str, parent_code: str) -> str:
        """Generates a diff text based on prompt and parent code"""
        # TODO: Implement actual diff generation logic
        return "<<<<<<< SEARCH\n# Original code\n=======\n# New code\n>>>>>>> REPLACE"

    async def _generate_new_code(self, prompt: str) -> str:
        """Generates new code from scratch based on prompt"""
        # TODO: Implement actual code generation logic
        return "# Generated code placeholder"

    def _apply_diff(self, parent_code: str, diff_text: str) -> str:
        """
        Applies a diff in the AlphaEvolve format to the parent code.
        Diff format:
        <<<<<<< SEARCH
        # Original code block
        =======
        # New code block
        >>>>>>> REPLACE
        
        Uses exact matching with whitespace and indentation preserved.
        """
        modified_code = parent_code
        # Improved regex to handle multiple diff blocks
        diff_pattern = re.compile(r'<<<<<<<\s+SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>>\s+REPLACE', re.DOTALL)
        
        # Process each diff block in order
        for match in diff_pattern.finditer(diff_text):
            search_block = match.group(1)
            replace_block = match.group(2)
            
            # First try exact match with original whitespace
            if search_block in modified_code:
                modified_code = modified_code.replace(search_block, replace_block, 1)
                continue
                
            # If exact match fails, try line-by-line matching
            search_lines = search_block.splitlines()
            parent_lines = modified_code.splitlines()
            
            for i in range(len(parent_lines) - len(search_lines) + 1):
                match_found = True
                for j in range(len(search_lines)):
                    if parent_lines[i + j].rstrip() != search_lines[j].rstrip():
                        match_found = False
                        break
                
                if match_found:
                    # Preserve indentation from parent code
                    indentation = parent_lines[i][:len(parent_lines[i]) - len(parent_lines[i].lstrip())]
                    replace_lines = []
                    for line in replace_block.splitlines():
                        if line.strip():
                            replace_lines.append(indentation + line)
                        else:
                            replace_lines.append(line)
                    
                    modified_code = '\n'.join(
                        parent_lines[:i] + 
                        replace_lines + 
                        parent_lines[i + len(search_lines):]
                    )
                    break
        
        return modified_code

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    def test_diff_application():
        agent = CodeGeneratorAgent()
        
        # Test 1: Simple exact match
        parent1 = """def hello():
    print("Hello, World!")
"""
        diff1 = """<<<<<<< SEARCH
    print("Hello, World!")
=======
    print("Hello, Universe!")
>>>>>>> REPLACE
"""
        expected1 = """def hello():
    print("Hello, Universe!")
"""
        result1 = agent._apply_diff(parent1, diff1)
        assert result1 == expected1, f"Test 1 failed\nExpected:\n{expected1}\nGot:\n{result1}"
        
        # Test 2: Line-by-line match with indentation
        parent2 = """class Test:
    def method1(self):
        return 1
        
    def method2(self):
        return 2
"""
        diff2 = """<<<<<<< SEARCH
    def method1(self):
        return 1
=======
    def method1(self):
        return 42
>>>>>>> REPLACE
"""
        expected2 = """class Test:
    def method1(self):
        return 42
        
    def method2(self):
        return 2
"""
        result2 = agent._apply_diff(parent2, diff2)
        assert result2 == expected2, f"Test 2 failed\nExpected:\n{expected2}\nGot:\n{result2}"
        
        # Test 3: Multiple diffs (fixed format)
        parent3 = """x = 1
y = 2
z = 3
"""
        diff3 = """<<<<<<< SEARCH
x = 1
=======
x = 10
>>>>>>> REPLACE
<<<<<<< SEARCH
z = 3
=======
z = 30
>>>>>>> REPLACE
"""
        expected3 = """x = 10
y = 2
z = 30
"""
        result3 = agent._apply_diff(parent3, diff3)
        assert result3 == expected3, f"Test 3 failed\nExpected:\n{expected3}\nGot:\n{result3}"
        
        print("All diff application tests passed successfully!")

    test_diff_application()
