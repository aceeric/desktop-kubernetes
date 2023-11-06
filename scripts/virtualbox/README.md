As of VirtualBox 7.0.10, the vboxmanage utility seemed more prone to locking errors:

```
VBoxManage: error: The machine 'foo' is already locked for a session (or being unlocked)
VBoxManage: error: Details: code VBOX_E_INVALID_OBJECT_STATE (0x80bb0007), component MachineWrap, interface IMachine, callee nsISupports
VBoxManage: error: Context: "LockMachine(a->session, LockType_Write)" at line 640 of file VBoxManageModifyVM.cpp
```

Hence the various sleep statements in these scripts.

