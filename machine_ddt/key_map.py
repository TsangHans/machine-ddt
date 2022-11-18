import mini_six.portable.win32.operation as operation

KEY_MAP = {
    "VK_LBUTTON": operation.VK_LBUTTON,  # 1	鼠标的左键
    "VK_RBUTTON": operation.VK_RBUTTON,  # 2	鼠标的右键
    "VK_CANCEL": operation.VK_CANCEL,  # 3	Ctrl+Break(通常不需要处理)
    "VK_MBUTTON": operation.VK_MBUTTON,  # 4	鼠标的中键（三按键鼠标)
    "VK_BACK": operation.VK_BACK,  # 8	Backspace键
    "VK_TAB": operation.VK_TAB,  # 9	Tab键
    "VK_CLEAR": operation.VK_CLEAR,  # 12	Clear键（Num Lock关闭时的数字键盘5）
    "VK_RETURN": operation.VK_RETURN,  # 13	Enter键
    "VK_SHIFT": operation.VK_SHIFT,  # 16	Shift键
    "VK_CONTROL": operation.VK_CONTROL,  # 17	Ctrl键
    "VK_MENU": operation.VK_MENU,  # 18	Alt键
    "VK_PAUSE": operation.VK_PAUSE,  # 19	Pause键
    "VK_CAPITAL": operation.VK_CAPITAL,  # 20	Caps Lock键
    "VK_ESCAPE": operation.VK_ESCAPE,  # 27	Ese键
    "VK_SPACE": operation.VK_SPACE,  # 32	Spacebar键
    "VK_PRIOR": operation.VK_PRIOR,  # 33	Page Up键
    "VK_NEXT": operation.VK_NEXT,  # 34	Page Domw键
    "VK_END": operation.VK_END,  # 35	End键
    "VK_HOME": operation.VK_HOME,  # 36	Home键
    "VK_LEFT": operation.VK_LEFT,  # 37	LEFT ARROW 键(←)
    "VK_UP": operation.VK_UP,  # 38	UP ARROW键(↑)
    "VK_RIGHT": operation.VK_RIGHT,  # 39	RIGHT ARROW键(→)
    "VK_DOWN": operation.VK_DOWN,  # 40	DOWN ARROW键(↓)
    "VK_Select": operation.VK_Select,  # 41	Select键
    "VK_PRINT": operation.VK_PRINT,  # 42
    "VK_EXECUTE": operation.VK_EXECUTE,  # 43	EXECUTE键
    "VK_SNAPSHOT": operation.VK_SNAPSHOT,  # 44	Print Screen键（抓屏）
    "VK_Insert": operation.VK_Insert,  # 45	Ins键(Num Lock关闭时的数字键盘0)
    "VK_Delete": operation.VK_Delete,  # 46	Del键(Num Lock关闭时的数字键盘.)
    "VK_HELP": operation.VK_HELP,  # 47	Help键
    "VK_0": operation.VK_0,  # 48	0键
    "VK_1": operation.VK_1,  # 49	1键
    "VK_2": operation.VK_2,  # 50	2键
    "VK_3": operation.VK_3,  # 51	3键
    "VK_4": operation.VK_4,  # 52	4键
    "VK_5": operation.VK_5,  # 53	5键
    "VK_6": operation.VK_6,  # 54	6键
    "VK_7": operation.VK_7,  # 55	7键
    "VK_8": operation.VK_8,  # 56	8键
    "VK_9": operation.VK_9,  # 57	9键
    "VK_A": operation.VK_A,  # 65	A键
    "VK_B": operation.VK_B,  # 66	B键
    "VK_C": operation.VK_C,  # 67	C键
    "VK_D": operation.VK_D,  # 68	D键
    "VK_E": operation.VK_E,  # 69	E键
    "VK_F": operation.VK_F,  # 70	F键
    "VK_G": operation.VK_G,  # 71	G键
    "VK_H": operation.VK_H,  # 72	H键
    "VK_I": operation.VK_I,  # 73	I键
    "VK_J": operation.VK_J,  # 74	J键
    "VK_K": operation.VK_K,  # 75	K键
    "VK_L": operation.VK_L,  # 76	L键
    "VK_M": operation.VK_M,  # 77	M键
    "VK_N": operation.VK_N,  # 78	N键
    "VK_O": operation.VK_O,  # 79	O键
    "VK_P": operation.VK_P,  # 80	P键
    "VK_Q": operation.VK_Q,  # 81	Q键
    "VK_R": operation.VK_R,  # 82	R键
    "VK_S": operation.VK_S,  # 83	S键
    "VK_T": operation.VK_T,  # 84	T键
    "VK_U": operation.VK_U,  # 85	U键
    "VK_V": operation.VK_V,  # 86	V键
    "VK_W": operation.VK_W,  # 87	W键
    "VK_X": operation.VK_X,  # 88	X键
    "VK_Y": operation.VK_Y,  # 89	Y键
    "VK_Z": operation.VK_Z,  # 90	Z键
    "VK_NUMPAD0": operation.VK_NUMPAD0,  # 96	数字键0键
    "VK_NUMPAD1": operation.VK_NUMPAD1,  # 97	数字键1键
    "VK_NUMPAD2": operation.VK_NUMPAD2,  # 98	数字键2键
    "VK_NUMPAD3": operation.VK_NUMPAD3,  # 99	数字键3键
    "VK_NUMPAD4": operation.VK_NUMPAD4,  # 100	数字键4键
    "VK_NUMPAD5": operation.VK_NUMPAD5,  # 101	数字键5键
    "VK_NUMPAD6": operation.VK_NUMPAD6,  # 102	数字键6键
    "VK_NUMPAD7": operation.VK_NUMPAD7,  # 103	数字键7键
    "VK_NUMPAD8": operation.VK_NUMPAD8,  # 104	数字键8键
    "VK_NUMPAD9": operation.VK_NUMPAD9,  # 105	数字键9键
    "VK_MULTIPLY": operation.VK_MULTIPLY,  # 106	数字键盘上的*键
    "VK_ADD": operation.VK_ADD,  # 107	数字键盘上的+键
    "VK_SEPARATOR": operation.VK_SEPARATOR,  # 108	Separator键
    "VK_SUBTRACT": operation.VK_SUBTRACT,  # 109	数字键盘上的-键
    "VK_DECIMAL": operation.VK_DECIMAL,  # 110	数字键盘上的.键
    "VK_DIVIDE": operation.VK_DIVIDE,  # 111	数字键盘上的/键
    "VK_F1": operation.VK_F1,  # 112	F1键
    "VK_F2": operation.VK_F2,  # 113	F2键
    "VK_F3": operation.VK_F3,  # 114	F3键
    "VK_F4": operation.VK_F4,  # 115	F4键
    "VK_F5": operation.VK_F5,  # 116	F5键
    "VK_F6": operation.VK_F6,  # 117	F6键
    "VK_F7": operation.VK_F7,  # 118	F7键
    "VK_F8": operation.VK_F8,  # 119	F8键
    "VK_F9": operation.VK_F9,  # 120	F9键
    "VK_F10": operation.VK_F10,  # 121	F10键
    "VK_F11": operation.VK_F11,  # 122	F11键
    "VK_F12": operation.VK_F12,  # 123	F12键
    "VK_NUMLOCK": operation.VK_NUMLOCK,  # 144	Num Lock 键
    "VK_SCROLL": operation.VK_SCROLL,  # 145	Scroll Lock键
}
