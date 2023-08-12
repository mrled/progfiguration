.. _hypotheses:

Hypotheses
==========

Progfiguration was written to test various hypotheses about configuration management, infrastructure as code, and programming in general.


* Imperative is better than declarative, even for infrastructure.
  Declarative documents impose severe limitations for dubious benefits.
  There are exceptions for simple record instantiation,
  but imperative programming can provide similar benefits when desired.
  Just being able to write code in my config would be a huge benefit.

  * A stronger version of this is that simply replacing YAML or HCL documents with Python code will work well.

  * Strengths of declarative:

      * easy things are easy, organized
      * **easy to read**, especially for someone who hasn't seen your project before. this is a huge strength in a decentralized project, or a big company. Declarative stuff is a common language that everyone understands.

  * Strengths of imperative:

      * You're going to end up doing a bunch of imperative gunk anyway in your nice declarative language, why not embrace it
      * No one is going to pretend that for loops in Terraform are nicer than just, a Python for loop, right? We don't have to debate that I hope?

  * Makes sense to use each for their strengths.

      * I'd default to Cloudformation for Route53 entries
      * But if I were setting up a complex system of VPCs, EC2 instances, IAM roles, etc, I'd probably look to the AWS API before too very long. I've done 5-10 2k line cloudformation files to set up infrastructure.

  * Ansible, Terraform, Cloudformation all are easy to hire for


* A featureful standard library is under-appreciated in modern programming.
  Python is worth using for its standard library alone.
  Its worth using the standard library over third party code most of the time.

  We do have some exceptions:

  * Runtime is more important that dev/build time
  * Pragmatically, some things just don't exist, like an encryption library that meets our needs, an ssh client, etc. We use age and ssh for this.
  * Some things the standard library chooses not to implement, like cryptography, ``requests``, package building, and ``pytz``.

* It's worth considering vendoring.
  We have to be careful not to shoot ourselves in the foot with security updates;
  vendoring ``requests`` is probably not a good idea.
* Building packages that run on target systems without any dependencies is worth it.
  We can bake some things in, a la "static linking",
  and this is good.
  (Really, Rust and Golang have shown how nice this is,
  I just wanted to do something similar in Python.)
  This isn't as problematic as true vendoring,
  and the benefits of a program that doesn't need a package manager to install can be powerful.
* We can build very fast imperative configuration management.
  Specifically, we can do better than Ansible.

* By default, hosts should be able to apply their own configuration without relying on bespoke infrastructure that the org has to maintain.
  Specifically, this means they should be able to download a package and run it, theoretically offline if the package doesn't inherently require Internet access, or perhaps on foreign networks without a VPN connection or special services.
  It means the the node should be able to decrypt its own secrets without a centralized secret store.
* (Eschewing a centralized secret store is not the right move everywhere, because there are security advantages to being able to revoke secrets without rebuilding packages. However, I think there's also benefit to being able to build packages that contain at least some secrets. For orgs where secret servers are worth their tradeoffs, the ability to build packages that contain at least some secrets is still a capability worth preserving.)

* It shouldn't be a black box.
  It should be a program you can modify.

* It should fit in one person's head.

