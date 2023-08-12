Imperative execution: Ansible vs progfiguration
===============================================

Ansible is _declarative_.
You write "documents" that describe the state you want your system to be in.

Progfiguration is _imperative_.
You write a program.

Ansible's declarative approach is very nice for simple tasks.
Starting a service or installing a package is easy to describe declaratively.

However, it requires someone to have written an imperative program to do the task you want.
If you want to do something that no one has written a module for,
you need to fall back to writing an imperative program yourself,
either in a script that you deploy and then run,
in ``cmd`` or ``shell`` tasks,
or in a custom module.

Progfiguration is imperative to begin with.
This sometimes requires more work than Ansible for simple tasks,
but in exchange,
handling anything that Ansible module developers didn't specifically account for is quite easy.

Progfiguration's approach also makes it easier to perform calculations on values.
In Ansible, you need to use the ``set_fact`` module to do this,
which is a bit awkward at best,
and for complex tasks is really confusing.
