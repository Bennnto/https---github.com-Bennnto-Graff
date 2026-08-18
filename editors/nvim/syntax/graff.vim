" Vim / Neovim Syntax Highlighting for Graff (.gf, .graff)
if exists("b:current_syntax")
  finish
endif

" Keywords
syn keyword graffKeyword let fix pub fn struct enum match case attempt fallback try ok assert assert_eq timeline rollback return break continue bind import if else while for in

" Types
syn keyword graffType int str float bool void

" Booleans
syn keyword graffBoolean true false

" Comments
syn match graffComment "#.*$"

" Strings ($"...", "...", and '...')
syn region graffString start='\$"' end='"' contains=graffEscape,graffInterpolation
syn region graffString start='"' end='"' contains=graffEscape
syn region graffString start="'" end="'" contains=graffEscape
syn match graffEscape "\\." contained
syn region graffInterpolation start="{" end="}" contained contains=TOP

" Numbers
syn match graffNumber "\v<\d+(\.\d+)?>"

" Operators
syn match graffOperator "::"
syn match graffOperator "->"
syn match graffOperator "=>"
syn match graffOperator "\.\."
syn match graffOperator "[+*/%^=!<>&|-]"

" Highlight Links
hi def link graffKeyword     Keyword
hi def link graffType        Type
hi def link graffBoolean     Boolean
hi def link graffComment     Comment
hi def link graffString      String
hi def link graffEscape      SpecialChar
hi def link graffInterpolation Identifier
hi def link graffNumber      Number
hi def link graffOperator    Operator

let b:current_syntax = "graff"
