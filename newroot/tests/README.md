## Note

The tests in this directory are not intended as  general-purpose unit tests. They contain parameters that are environment-specific and context-specific. If you want to run these tests you will have to edit some params in the test scripts in ways that make sense for your environment. For example:

1. The `test-clone-mm` script has a hard-coded path ref to the directory where I locate all the Virtual Box VDIs and associated files.

2. Many of the scripts have hard-coded VM IPs and names based on testing at a certain point in time. If the same test was re-performed, the IP address or VM name might change, etc.

3. Some scripts have the primary network interface name from my host machine. Yours would likely be different.

And so on...