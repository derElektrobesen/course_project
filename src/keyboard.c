#include "keyboard.h"

/**
  * Структура определяет одну клавишу
  */
struct key_map {
	const unsigned char key;
	const unsigned char codes[MAX_CODES];
	const int count;
};

/**
  * Структура хранит все необходимые перемнные
  */
static struct {
	unsigned char current_code_index;
	unsigned char last_key;
	bool extra_key_pressed;

	unsigned long jiff;
	struct key_map key_map[KEYS_COUNT];
} kbd = { 	
	.last_key = 0,
	.jiff = 0,
	.key_map = KEY_MAP,
	.extra_key_pressed = false,
};


/**
  * Ф-ия возвращает для клавиши key, соответствующую
  * ей структуру в массиве kbd.key_map
  */
inline static const struct key_map *find_map(unsigned char key)
{
	const struct key_map *r = NULL;
	int i;

	for (i = 0; !r && i < KEYS_COUNT; i++)
		if (kbd.key_map[i].key == key)
			r = &kbd.key_map[i];

	return r;
}

#define MBP_PROCESS		1
#define MBP_EXIT		0
#define MBP_P_EXIT	   -1

/**
  * Ф-ия проверяет нажатую клавишу на предмет обработки.
  * Возвращает MBP_PROCESS, если клавишу надо обработать,
  * 		   MBP_EXIT, если передавать клавишу драйверу выше не надо,
  *			   MBP_P_EXIT, если клавиша не участвует в обработке, и ее должен
  *					обработать драйвер выше.
  */
inline static int must_be_processed(unsigned char data)
{
	int i;
	for (i = 0; i < KEYS_COUNT; i++) {
		if (data == kbd.key_map[i].key)
			return MBP_PROCESS;
		if (data == SHIFT(kbd.key_map[i].key))
			return MBP_EXIT;
	}
	return MBP_P_EXIT;
}

/**
  * Ф-ия обрабатывает нажатую клавишу и 
  * посылает ее на обработку драйверу выше.
  */
static void process_key(unsigned char data, unsigned char str,
		struct serio *serio)
{
	const struct key_map *map;
	bool err = true;
	unsigned char c;

	if (!(map = find_map(data)))
		return;

	if (time_after(jiffies, kbd.jiff + MAX_DELAY)) 
		kbd.last_key = 0x00;
	
	if (kbd.last_key != data)
		kbd.last_key = data;
	else {
		if (++kbd.current_code_index < map->count)
			err = false;
		send_key(serio, BACKSPACE_KEY, str);
	}
	kbd.jiff = jiffies;

	if (err)
		kbd.current_code_index = 0;

	c = map->codes[kbd.current_code_index];

	if (IS_SHIFT(c)) {
		serio_interrupt(serio, BTN_PUSH(SHIFT_KEY), STR_TO_DFL(str));
		send_key(serio, RM_SHIFT(c), str);
		serio_interrupt(serio, BTN_POP(SHIFT_KEY), STR_TO_DFL(str));
	} else 
		send_key(serio, c, str);
}

/**
  * Ф-ия фильтрует нажатую клавишу, ее код, и при необходимости
  * меняет ее.
  */
static bool filter(unsigned char data, unsigned char str, 
				   struct serio *serio)
{
	int process;
	bool result = true;

	if (!IS_KEYBRD(str))
		return false;

	if (kbd.extra_key_pressed) {
		kbd.extra_key_pressed = false;
		return false;
	}

	if (IS_EXTRA_KEY(data)) {
		kbd.extra_key_pressed = true;
		return false;
	}

	process = must_be_processed(data);

	if (process)
		log("data: 0x%x; str: 0x%x", data, str);

	if (process == MBP_PROCESS)
		process_key(data, str, serio);
	else if (process == MBP_P_EXIT) {
		result = false;
		kbd.last_key = 0;
	}

	return result;
}

/**
  * Ф-ия инициализации драйвера
  */
int init_keybrd(void)
{
	return i8042_install_filter(filter);
}

/**
  * Ф-ия отключения драйвера
  */
void unreg_keybrd(void)
{
	i8042_remove_filter(filter);
}

