======= ========================================================================
Command                                  Action
======= ========================================================================
 ``A``  Add a child to the current node with the value taken from the next byte
        in the program (usually you should use literals instead)
------- ------------------------------------------------------------------------
 ``B``  Remove the first child from the current node
------- ------------------------------------------------------------------------
 ``C``  Set second register to:
        
        - child of current node if value of first register is zero or less

        - sibling of current node otherwise
------- ------------------------------------------------------------------------
 ``D``  Set a pointer to point to the node in second register:

        - current node's child's sibling if value of first register is one or
          less

        - current node's sibling's sibling otherwise
------- ------------------------------------------------------------------------
 ``E``  Set the value of curent node to the sum of all values in its subtree
------- ------------------------------------------------------------------------
 ``F``  Negate values of all nodes in the current node's subtree
------- ------------------------------------------------------------------------
 ``G``  Set the value of the first register to the count of current node's
        children
------- ------------------------------------------------------------------------
 ``H``  Swap nodes between the two registers
------- ------------------------------------------------------------------------
 ``I``  Perform the "rotate down" operation on the current node
------- ------------------------------------------------------------------------
 ``J``  Perform the "rotate up" operation on the current node
------- ------------------------------------------------------------------------
 ``K``  Set first register to a deep copy of the current node's subtree
------- ------------------------------------------------------------------------
 ``L``  Set first register to the current node
------- ------------------------------------------------------------------------
 ``M``  Move up the parent pointer of current node (inconsistent, don't use)
------- ------------------------------------------------------------------------
 ``N``  Move to the child of current node
------- ------------------------------------------------------------------------
 ``O``  Move to the sibling of current node
------- ------------------------------------------------------------------------
 ``P``  Move to the node in the first register
------- ------------------------------------------------------------------------
 ``Q``  Jump in the program by the value in the first register:

        - if the current node has value zero jump backward

        - otherwise jump backward
------- ------------------------------------------------------------------------
 ``R``  Output the lowest 8 bits of the value of the current node as a byte
------- ------------------------------------------------------------------------
 ``S``  Load a byte to the value of the current node
------- ------------------------------------------------------------------------
 ``T``  Set the value of the current node to the product of values in registers
------- ------------------------------------------------------------------------
 ``U``  Prettyprint the subtree of the current node
------- ------------------------------------------------------------------------
 ``V``  Go to the root node of the tree
------- ------------------------------------------------------------------------
 ``W``  Jump in the program by the value in the first register if the value of
        the current node is zero
======= ========================================================================
