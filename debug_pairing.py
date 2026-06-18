import traceback
try:
    from human.systems.social.pairing_system import PairingSystem
    import inspect
    print(inspect.getsource(PairingSystem))
except Exception as e:
    traceback.print_exc()
