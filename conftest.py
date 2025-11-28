# Needed for pytest to add CLI options to facilitate the production of control values (especially images)
def pytest_addoption(parser):
    parser.addoption("--gen-ref", action="store_true", help="Don't perform checks, instead generate reference image (override if exists) with 1024 rays per pixel")
    parser.addoption("--gen-hist", action="store_true", help="Don't perform checks, instead generate (override if exists) error histograms relative to reference image")
    parser.addoption("--gen-thres", action="store_true", help="Don't perform checks, instead generate error threshold (replace if exists)")
    parser.addoption("--save", action="store_true", help="In addition of checks, also save all test images and error histograms to ./save/ directory")
    parser.addoption("--host", type=str, default="localhost", help="When using surrender_client_pytest class or s fixture, choose host to connect to")
    parser.addoption("--port", type=int, default=5151, help="When using surrender_client_pytest class or s fixture, choose port to connect to")
