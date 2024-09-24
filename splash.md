# Welcome to a Python 3 Simple Wiki

### Useful (internal) Links

* [Guide](Guide) to our Markdown dialect
* [TODO](TODO)

## Motivation


<strong>Moin2</strong> is not ready and I needed a simple &lt;sup&gt;Wiki&lt;/sup&gt; with authentication for a small group and ~~a WYSIWYG~~ an editor like __[Pell](https://github.com/jaredreich/pell)__
&lt;br&gt;
### Examples
Here is an example pages copied from wikipedia into the Markdown format, and rendered by this program. (from wiki-in-a-flask)<p></p>
<ul>
   <li><a href="/wiki/ISO_8601">ISO 8601</a></li>
</ul>

And here is the source to that same pages in <a href="https://en.wikipedia.org/wiki/Markdown#Example">Markdown</a>.

<ul>
   <li><a href="/wiki/md/ISO_8601">ISO 8601 Source</a></li>
</ul>

Files in the <em>/static/</em> folder are accessible by the server either as /static or /wiki/static, to cover two different nginx configurations.

Files that you have uploaded can be listed using [this bookmark](/wiki/upload/@me)