##        Vimpy ~ Python auto-import plugin for Vim

1. Description                                          
2. Options                                              
3. Commands                                             
4. Requirements                                         
5. Contact                                              


### 1. Description                                         

Vimpy is a vim-plugin which can be used to (semi) automatically add 
new import lines to your python scripts. 
When you run vimpy it will evaluate the line at the cursor position. If it 
finds any missing / undefined names it will try to automagically resolve 
what (sub)module(s) is/are missing and add the needed import lines to the top 
of the python script.

When the import line to be added is in the simple / direct format (eg. import
os) impy will not need any help unless it can't find the module in the
$PYTHONPATH. 
Relative imports (eg. from foo import blah) are more tricky. If the relative 
import is from a module that has already been imported / added as an
importline impy should be fine. If it's a new module however vimpy will most
likely need some help and (optionally) prompt for the module the relative
import is importing from.

Vimpy follows the PEP8 guidelines. Imports are grouped in the following order:
stdlib imports, third-party imports and local imports with a blank line 
between each section and two blank lines after the last importline.

### 2. Options                                                 

This option controls whether impy will ask for help when it cannot resolve
a relative import by itself.

    let g:vimpy_prompt_resolve = 1

If this option is set vimpy will remove import lines for unused modules.

    let g:vimpy_remove_unused = 1

### 3. Commands                                               
                                                    
Checks the line at the cursor's position for new imports.
    
    :VimpyCheckLine

### 4. Requirements

Vimpy relies on 'pyflakes' for its missing import decection magic. This
third-party module can be installed using pip or downloaded from
pypi: https://pypi.python.org/pypi/pyflakes.

### 5. Contact

Plugin github page @ http://github.com/dbsr/vimpy

You can contact me at dydrmntion -AT- gmail -DOT- com.
