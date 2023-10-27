import glfw
import OpenGL.GL as gl
import time

window_size = 512
num_click = 0

point_A = [0, 0, 0]
point_B = [0, 0, 0]
point_C = [0, 0, 0]

Color_A = [1, 0, 0] #Red
Color_B = [0, 1, 0] #Green
Color_C = [0, 0, 1] #Blue

def main():

    # initialize glfw
    if not glfw.init():
        print("Glfw window can't be initialized")
        return

    window = glfw.create_window(window_size, window_size, "Graphics HW#2 - SkyKim", None, None)

    if not window:
        glfw.terminate()
        print("Glfw window can't be created")
        return

    glfw.set_window_pos(window, 0, 0)
    glfw.make_context_current(window)
    
    glfw.set_mouse_button_callback(window, button_callback)
    gl.glClearColor(0.0, 0.0, 0.0, 1.0) # background color is black
        
    # open window and draw
    while not glfw.window_should_close(window): 
        display()
        glfw.poll_events()
        glfw.swap_buffers(window)
        
    # terminate program        
    glfw.terminate()
    
def display():
    global point_A, point_B, point_C, num_click
    
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    
    glPoints(point_A[0], point_A[1], Color_A) # draw pointA        
    glPoints(point_B[0], point_B[1], Color_B) # draw pointB
    glPoints(point_C[0], point_C[1], Color_C) # draw pointC
    
    #Fill the inside of a triangle with a color (alpha, beta, gamma)
    if num_click == 3:
        for px in range(1,window_size):
            for py in range(1,window_size):
                point_P = [px, py, 0]
                alpha, beta, gamma, draw_flag = sanity_check(point_A, point_B, point_C, point_P)
                
                if draw_flag == True: # If the point is inside a triangle, fills the color with alpha, beta, and gamma values
                    rgb = (alpha * (Color_A[0] + Color_B[0] + Color_C[0]), beta * (Color_A[1] + Color_B[1] + Color_C[1]), gamma * (Color_A[2] + Color_B[2] + Color_C[2]))
                    glPoints(px, py, rgb)

def glPoints(x, y, color):
    vx = (x / (window_size / 2.0)) - 1.0
    vy = (y / (window_size / 2.0)) - 1.0

    gl.glBegin(gl.GL_POINTS)
    gl.glColor3f(color[0], color[1], color[2])
    gl.glVertex2f(vx, vy)
    gl.glEnd()
    
def dot3f(vector_a, vector_b):
    return vector_a[0] * vector_b[0] + vector_a[1] * vector_b[1] + vector_a[2] * vector_b[2]

def cross3f(vector_a, vector_b):
    return vector_a[1] * vector_b[2] - vector_a[2] * vector_b[1], vector_a[2] * vector_b[0] - vector_a[0] * vector_b[2], vector_a[0] * vector_b[1] - vector_a[1] * vector_b[0]

def tuple_subtraction(vector_a, vector_b):
    return (vector_a[0] - vector_b[0], vector_a[1] - vector_b[1], vector_a[2] - vector_b[2])

def sanity_check(point_A, point_B, point_C, point_P):

    n = cross3f(tuple_subtraction(point_B, point_A), tuple_subtraction(point_C, point_A))
    n_a = cross3f(tuple_subtraction(point_C, point_B), tuple_subtraction(point_P, point_B))
    n_b = cross3f(tuple_subtraction(point_A, point_C), tuple_subtraction(point_P, point_C))
    n_c = cross3f(tuple_subtraction(point_B, point_A), tuple_subtraction(point_P, point_A))
   
    alpha = dot3f(n, n_a) / dot3f (n, n)
    beta = dot3f(n, n_b) / dot3f (n, n)
    gamma = dot3f(n, n_c) / dot3f (n, n)
        
    if boundary_check(alpha) and boundary_check(beta) and boundary_check(gamma):
        return alpha, beta, gamma, True
    else:
        return alpha, beta, gamma, False

def boundary_check(value):
    if (value < 0) or (value > 1):
        return False
    else:
        return True

def button_callback(window, button, action, mod):
    global num_click
    global point_A, point_B, point_C

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            xpos, ypos = glfw.get_cursor_pos(window)

            gl_xpos = xpos
            gl_ypos = window_size-ypos

            if num_click == 0:
                point_A = (gl_xpos, gl_ypos, 0)
                num_click = num_click + 1
            elif num_click == 1:
                point_B = (gl_xpos, gl_ypos, 0)
                num_click = num_click + 1
            elif num_click == 2:
                point_C = (gl_xpos, gl_ypos, 0)
                num_click = num_click + 1
            elif num_click == 3: # run the sanity_check for a new point
                alpha, beta, gamma, draw_flag = sanity_check(point_A, point_B, point_C, (gl_xpos, gl_ypos, 0))
                print(f'alpha={alpha}, beta={beta}, gamma={gamma}, draw_flag={draw_flag}')

if __name__ == "__main__":
    main()