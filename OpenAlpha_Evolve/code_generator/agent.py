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
        
        generated_code = await self._call_llm(prompt, parent_code, temperature, max_length)
        
        if syntax_validation:
            try:
                ast.parse(generated_code)
            except SyntaxError as e:
                logger.warning(f"Syntax error in generated code: {e}")
                generated_code = self._fix_indentation(generated_code)
                try:
                    ast.parse(generated_code)
                except SyntaxError: # Reverted e2 to e
                    logger.error("Failed to fix syntax errors in generated code")
                    raise
                    
        return generated_code

    async def _call_llm(self, prompt: str, parent_code: str, temperature: float, max_length: int) -> str:
        """Call the LLM to generate code with proper structure"""
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
            
            if stripped.startswith(('return ', 'break ', 'continue ', 'pass ')):
                fixed_lines.append('    ' * indent_level + stripped)
                continue
                
            if stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except ', 'finally:')):
                fixed_lines.append('    ' * indent_level + stripped)
                indent_level += 1
                continue
                
            # Corrected condition for else, elif, except, finally
            if stripped == 'else:' or \
               stripped.startswith('elif ') or stripped == 'elif:' or \
               stripped.startswith('except ') or stripped == 'except:' or \
               stripped == 'finally:':
                indent_level -= 1
                fixed_lines.append('    ' * indent_level + stripped)
                indent_level += 1
                continue
                
            if stripped:
                fixed_lines.append('    ' * indent_level + stripped)
            else:
                fixed_lines.append('')
                
        return '\n'.join(fixed_lines)
        
        # Unreachable code block, removed for clarity and to avoid confusion
        # if parent_code:
        #     async def _generate_diff(self, prompt: str, parent_code: str) -> str:
        #         """Generate a diff between parent code and new version"""
        #         return "# Generated diff placeholder"
        #     return self._apply_diff(parent_code, "#diff_text_placeholder") # diff_text was undefined
        # else:
        #     async def _generate_new_code(self, prompt: str) -> str:
        #         """Generate new code from prompt"""
        #         return "# Generated new code placeholder"

    async def _generate_diff(self, prompt: str, parent_code: str) -> str:
        """Generates a diff text based on prompt and parent code"""
        return "<<<<<<< SEARCH\n# Original code\n=======\n# New code\n>>>>>>> REPLACE"

    async def _generate_new_code(self, prompt: str) -> str:
        """Generates new code from scratch based on prompt"""
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
        diff_pattern = re.compile(r'<<<<<<<\s+SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>>\s+REPLACE', re.DOTALL)
        
        for match in diff_pattern.finditer(diff_text):
            search_block = match.group(1)
            replace_block = match.group(2)
            
            if search_block in modified_code:
                modified_code = modified_code.replace(search_block, replace_block, 1)
                continue
                
            search_lines = search_block.splitlines()
            parent_lines = modified_code.splitlines()
            
            for i in range(len(parent_lines) - len(search_lines) + 1):
                match_found = True
                for j in range(len(search_lines)):
                    if parent_lines[i + j].rstrip() != search_lines[j].rstrip():
                        match_found = False
                        break
                
                if match_found:
                    indentation = parent_lines[i][:len(parent_lines[i]) - len(parent_lines[i].lstrip())]
                    replace_lines_with_indent = []
                    for line in replace_block.splitlines():
                        if line.strip():
                            replace_lines_with_indent.append(indentation + line)
                        else:
                            replace_lines_with_indent.append(line)
                    
                    modified_code = '\n'.join(
                        parent_lines[:i] + 
                        replace_lines_with_indent + 
                        parent_lines[i + len(search_lines):]
                    )
                    break
        
        return modified_code
