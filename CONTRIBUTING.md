To add support for a different model of Alienware computer, do the following:
----------------------------------------------------------------------------

1. Copy `alienfx/core/controller_m17x.py` to `controller_<your-computer-name>.py`
   in the same directory, and modify it using the original file as a reference.

2. At the top of `alienfx/core/prober.py`, add an import statement to import your
   new controller module created in step 1. This should be done at the docstring
   """ Import all subclasses of AlienFXController here. """. 

3. Modify `data/etc/udev/rules.d/10-alienfx.rules` to add a line for the VID and 
   PID corresponding to the AlienFX USB controller on your computer.

4. Test your modifications, and please submit a patch!


Please pull request all code to the LATEST version! Thanks!
--------------------------------------------------------

**Working on your first Pull Request?** You can learn how from this *free* series [How to Contribute to an Open Source Project on GitHub](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github)
