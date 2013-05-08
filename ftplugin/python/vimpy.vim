" File: Autovimpy.vim
" Author: dydrmntion@gmail.com

if exists('vimpy_did_vim')
    finish
endif
let g:vimpy_did_vim = 1


if !exists('g:vimpy_prompt_resolve')
    let g:vimpy_prompt_resolve = 1
endif

" Debug log
let s:vimpy_debug_log = 1

" Make sure we have pyflakes
let s:have_flake = 1
python << EOF
try:
    import pyflakes
except ImportError:
    vim.eval('let s:have_flake = 0')
EOF
if !s:have_flake
    echo "vimpy needs the python module pyflakes."
    finish
endif

" Expand our path
python << EOF
import vim, os, sys
new_path = vim.eval('expand("<sfile>:h")')
sys.path.append(new_path)
import vimpy
from vimpy import vimpy_
if bool(int(vim.eval('s:vimpy_debug_log'))):
    vimpy.init_log()
EOF

function! s:DovimpyCheckLine()
    exe 'py vimpy_.do_vimpy(' . line(".") . ')'
endfunction

command! -bar VimpyCheckLine call s:DovimpyCheckLine()
