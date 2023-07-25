Sphinx and progfiguration
=========================

We use Sphinx for documentation.
Here are a few notes on how we use it.

* Sphinx doesn't automatically generate documentation for every module,
  and while you can use the ``automodule`` extension to do so,
  it's kind of hacky and I couldn't make it work for me.

  See <https://stackoverflow.com/questions/2701998/automatically-document-all-modules-recursively-with-sphinx-autodoc/62613202#62613202>
  for what I tried.

  Instead I'm using readthedocs' ``sphinx-apidoc`` extension, which seems to work.

* I like the default Alabaster theme, but its sidebar was a CSS overflow mess.
  Furo worked great out of the box.
