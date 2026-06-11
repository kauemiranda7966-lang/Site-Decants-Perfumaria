"""Compatible entry point for the Decant's Perfumaria application."""
import sys
import decants_app as _app

if __name__ == "__main__":
    _app.main()
else:
    sys.modules[__name__] = _app
