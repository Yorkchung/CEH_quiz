import os

def setup():
    os.system('pip install -r requirements.txt')

def check_folder():
    if not os.path.isdir("./test/"):
        os.mkdir("./test")
    if not os.path.isdir("./pdf/"):
        os.mkdir("./pdf")
    if not os.path.isdir("./report/"):
        os.mkdir("./report")

if __name__ == '__main__':
    setup()
    check_folder()
