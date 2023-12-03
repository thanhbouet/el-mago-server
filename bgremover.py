from rembg import remove
from PIL import Image

def remove_bg(i_path, o_path):
    input = Image.open(i_path)
    output = remove(input)
    output.save(o_path)
    
    
if __name__ == '__main__':
    remove_bg(r"D:\hoctap\Python\demo-flask\res\thanh.jpg",r"D:\hoctap\Python\demo-flask\res\thanh_removed.png")