Guide :joy:
=======

#### Table of Contents

1. [Headings](#headings)
3. [Formatting](#format) &amp; Emphasis
4. [Blockquote](#blockquote)
5. [Images](#images)
6. [Links](#links)
7. [Code](#code) [TO-DO]
8. [Lists](#lists)
    - [Ordered List](#orderedlist)
    - [Unordered List](#unorderedlist)
    - [Mixed List](#mixedlist)
9. [Table](#table)
10. [Task List](#tasklist)
11. [Footnote](#footnote)
12. [Jump to section](#sectionjump)
13. [Horizontal Line](#horizontalline)
14. [HTML](#html)

---

# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

## Formatting and Emphasis

| Example | How it is done |
| :--     | :- |
| Using two asterisks **this text is bold**. | \*\*this text is bold\*\*   
|Two underscores __work as well__. | __&nbsp;&nbsp;&nbsp;&nbsp;__work as well__&nbsp;&nbsp;&#8203;&nbsp;&nbsp;__    
|Let's make it *italic now*.  | \*italic now\*  
|Can we combine **_both of that_?** | Absolutely. \*\*\_both of that\_?\*\*    
|What if I want to ~~strikethrough~~? | ~\~strike~\~    
| I need to highlight these ==very important words==. | [Not implemented yet]  
|Subscript: H~2~O.  | [TODO]
|Superscript: X^2^.  | [TODO]

#### escaping and escapes
If you want to escape a strike-through then you can ~&#8203;\~do it~&#8203;\~ with a backslash between the tildes.       
To escape an  \_\\\_underline\_\\\_ is done with a backslash between the underscores   
and you can just escape the ampersand in &amp;&#8203;amp;#1f600​​; with &lt;&#8203;zws&gt; &amp;&#8203;#128512; =&gt; 😀

or you can do it with a [sneaky] zero-width space using the &lt;&#8203;zws&gt; tag   
[**N.B.**: if you end a line with '.  ' ({stop}+{space}+{space}) it causes a new-line].  
[**TODO**: blockquotes].  

&gt; This is a blockquote.  
&gt; Want to write on a new line with space between?  
&gt;
&gt; &gt; And nested? No problem at all.  
&gt; &gt;
&gt; &gt; &gt; PS. you can **style** your text _as you want_.  

##### nbsp  
&lt;​nbsp​&gt; &nbsp; will add a space to a line  
 &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;  and multiple can be used to indent a line  

##### zero-width space

&lt;&#8203;zws&gt; will be converted into a zero-width space &amp;\#8203;​​ 

## Images
#### Internal images
![TODO](/static/favicon.ico "Text displayed on hover")

#### External images
![wiki](https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/103px-Wikipedia-logo-v2.svg.png "Wikimedia logo")

#### Image upload
[**TODO**: image_upload]

## Links
[markdown-cheatsheet]: https://github.com/im-luka/markdown-cheatsheet
[docs]: https://github.com/adam-p/markdown-here


### wiki admin
 The `.env` file at the root has the strings for the wiki (so you can convert to your own language).


## Lists


### Ordered List

1. HTML
2. CSS
3. Javascript
4. React
7. I'm Frontend Dev now 👨🏼‍🎨

----
<a>

### Unordered List

- Mithril.js
+ React
* Python
- Learning Rust ⌛️

-----

### Mixed List
1. Learn Basics
      1. HTML
      2. CSS
      7. Javascript
2. Learn One Framework
   - React 
     - Router
     - Redux
   * Vue
   + Svelte

----
### deep list
1. First list item
    - First nested list item [4 spaces in]
        - Second nested list item
            - Third nested list item
                - Fourth nested list item
                    - Fifth nested list item

* First list item
    - First nested list item [4 spaces in]
       - Second nested list item
           - Third nested list item
               - Fourth nested list item
                   - Fifth nested list item
* asterisk(s) will keep found of ordered list
* for each entry
---

[**TODO**:enable footnotes with anchors]
Here's a sentence with a footnote. [^1]


## Table
Great way to display well-arranged data. Use "|" symbol to separate columns and ":" symbol to align row content.

| Left Align (default) | Center Align | Right Align |
| :------------------- | :----------: | ----------: |
| Mithril.JS           | React.js     | MariaDB     |
| Rust                 | Bun          | MongoDB     |
| Vue.js               | Zig          | Redis       |

---

## Task List
Tasks are created using lists that start with  '- \[ \]' or '- \[x\]'

<pre>- [x] Write Markdown Guide  

- [ ] Extend Markdown to do the things that we need  

- [ ] Live happily ever after  

produces the following task list:
</pre>

- [x] Write Markdown Guide
- [ ] Extend Markdown to do the things that we need
- [ ] Live happily ever after

...

##### Section with some ID

First Horizontal Line

***

Second One

-----

Third

_________


### Some raw HTML tags are permitted

<h3>such as heading tags</h3>
<p>Paragraphs...</p>  
<em>centering image</em>  
   
HREF anchors </a><a href="https://github.com/alexxroche/python3-simple-wiki">p3sw on GitHub</a>   
<strong>strong</strong>    
  → Easy  
  → And simple  
  → lists


### but not the following:
&lt;hr /&gt;   
&lt;br&gt;   
&lt;br/&gt;   
&lt;hr/&gt;   
&lt;hr&gt;   
&lt;img src="auto-generated-path-to-file-when-you-upload-image" width="200"&gt;   
&lt;br /&gt;   
&lt;span&gt;span&lt;/span&gt;   
&lt;details&gt;
  &lt;summary&gt;details &gt; summary&lt;/summary&gt;
&lt;/details&gt;


## Things that haven't been implemented yet

### anchors and custom tag IDs

[Jump to a section with custom ID](#some-id)


### code and backtick inline formatting
 
    Backticks inside backticks? `` `No problem.` ``

    ```
    {
      learning: "Markdown",
      showing: "block code snippet"
    }
    ```

    ```js
    const x = "Block code snippet in JS";
    console.log(x);
    ```

{
  learning: "Markdown",
  showing: "block code snippet"
}



[**TODO**:background colour + for highlighting]
The background color is `#ffffff` for light mode and `#000000` for dark mode.

[**TODO**:foreground colour]
to paint the text

#### External guides
* [A guide](https://www.markdownguide.org/cheat-sheet/)
* [github guide](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)


#### footnotes
[^1]: This is the footnote. 
