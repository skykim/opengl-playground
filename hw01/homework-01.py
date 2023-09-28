import glfw
import OpenGL.GL as gl
from PIL import Image
import os

#(p4)     (p3)
# .-------.
# |       |
# |       |
# .-------.
#(p1)     (p2)

p4_xpos = 0
p4_ypos = 0
p2_xpos = 0
p2_ypos = 0

mouse_left_button_pressed = False

def main(image_filename):
    global image, image_width, image_height
    
    # read an image by PIL
    image = Image.open(image_filename).convert("RGBA").transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    image_data = image.tobytes()
    image_width, image_height = image.size

    # initialize glfw
    if not glfw.init():
        print("Glfw window can't be initialized")
        #return

    window = glfw.create_window(image_width, image_height, "Graphics HW#1 - SkyKim", None, None)

    if not window:
        glfw.terminate()
        print("Glfw window can't be created")
        #return

    glfw.set_window_pos(window, 0, 0)
    glfw.make_context_current(window)

    # set mouse callback functions
    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_mouse_button_callback(window, button_callback)

    # generate 2D Texture
    texture_id = get_texture_from_image_data(image_data)
    
    # open window and draw
    while not glfw.window_should_close(window):

        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        draw_texture(texture_id)
        draw_crop_rect()
        gl.glDisable(gl.GL_TEXTURE_2D)
        
        glfw.poll_events()
        glfw.swap_buffers(window)

    # terminate program        
    glfw.terminate()
    
def get_texture_from_image_data(image_data):
    texture_id = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, image_width, image_height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_data)
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
    
    return texture_id

def draw_texture(texture_id):
    gl.glColor3f(1.0, 1.0, 1.0) #set color

    gl.glBegin(gl.GL_QUADS)

    gl.glTexCoord2f(0, 0)
    gl.glVertex2f(-1, -1)    
    gl.glTexCoord2f(1, 0)
    gl.glVertex2f(1, -1)
    gl.glTexCoord2f(1, 1)
    gl.glVertex2f(1, 1)
    gl.glTexCoord2f(0, 1)
    gl.glVertex2f(-1, 1)

    gl.glEnd()
    
def draw_crop_rect():
    gl.glColor3f(1.0, 0.0, 0.0) #set red color
    gl.glLineWidth(3.0) #set linewidth 3

    gl.glBegin(gl.GL_LINES)
    
    gl.glVertex2f(p4_xpos, p2_ypos) #p1
    gl.glVertex2f(p2_xpos, p2_ypos) #p2
    gl.glVertex2f(p2_xpos, p2_ypos) #p2
    gl.glVertex2f(p2_xpos, p4_ypos) #p3
    gl.glVertex2f(p2_xpos, p4_ypos) #p3
    gl.glVertex2f(p4_xpos, p4_ypos) #p4
    gl.glVertex2f(p4_xpos, p4_ypos) #p4
    gl.glVertex2f(p4_xpos, p2_ypos) #p1
    
    gl.glEnd()

def get_position_from_window_to_opengl(xpos, ypos):
    halfsize_width = image_width/2.0
    halfsize_height = image_height/2.0    
    xpos_next =  (xpos-halfsize_width)/halfsize_width
    ypos_next = (ypos-halfsize_height)/halfsize_height    
    return xpos_next, -ypos_next

def get_position_from_opengl_to_window(xpos, ypos):
    halfsize_width = image_width/2.0
    halfsize_height = image_height/2.0    
    xpos_next = xpos*halfsize_width + halfsize_width
    ypos_next = -ypos*halfsize_height + halfsize_height    
    return xpos_next, ypos_next

def crop_and_save_image():
    global image, image_filename    
    crop_area = (min(p2_xpos, p4_xpos), max(-p2_ypos, -p4_ypos), max(p2_xpos, p4_xpos), min(-p2_ypos, -p4_ypos))
    crop_area = get_position_from_opengl_to_window(crop_area[0], crop_area[1]) + get_position_from_opengl_to_window(crop_area[2], crop_area[3])            
    cropped_img = image.crop(crop_area).transpose(Image.Transpose.FLIP_TOP_BOTTOM)        
    cropped_img.save(os.path.basename(image_filename) + "_cropped.png")    
    print('save a cropped.png')

def press_left_mouse_button():
    global mouse_left_button_pressed
    mouse_left_button_pressed = True

def release_left_mouse_button():
    global mouse_left_button_pressed
    mouse_left_button_pressed = False    
    xpos, ypos = get_position_from_opengl_to_window(p4_xpos, p4_ypos) 
    print(f'end to draw:{xpos}, {ypos}')

def update_p2_pos(xpos, ypos):
    global p2_xpos, p2_ypos
    if mouse_left_button_pressed == True:
        p2_xpos, p2_ypos = get_position_from_window_to_opengl(xpos, ypos)
        #print('mouse cursor moving: (%f, %f)' % (p2_xpos, p2_ypos))

def start_p4_pos(xpos, ypos):
    global mouse_left_button_pressed, p4_xpos, p4_ypos, p2_xpos, p2_ypos
    
    if mouse_left_button_pressed == False:
        press_left_mouse_button()  
        p4_xpos, p4_ypos = get_position_from_window_to_opengl(xpos, ypos)
        p2_xpos = p4_xpos
        p2_ypos = p4_ypos
        xpos, ypos = get_position_from_opengl_to_window(p4_xpos, p4_ypos)            
        print(f'start to draw a rect:{xpos}, {ypos}')
        
def key_callback(window, key, scancode, action, mods):    
    if key == glfw.KEY_SPACE and action == glfw.PRESS:
        crop_and_save_image()

def cursor_callback(window, xpos, ypos):
    update_p2_pos(xpos, ypos)

def button_callback(window, button, action, mod):
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            xpos, ypos = glfw.get_cursor_pos(window)
            start_p4_pos(xpos, ypos)
        elif action == glfw.RELEASE:
            release_left_mouse_button()

if __name__ == "__main__":
    image_filename = './simpson.png'
    main(image_filename)