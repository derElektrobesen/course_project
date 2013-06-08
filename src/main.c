#include "main_header.h"
#include "keyboard.h"

/**
  * Конструктор
  */
static int __init init_proc(void)
{
	int r = 0;
	log("Loading driver...");
	r = init_keybrd();
	if (r != 0)
		hint("Error loading driver");
	else
		hint("Driver loaded");
	return r;
}

/**
  * Деструктор
  */
static void __exit exit_proc(void)
{
	log("Stopping driver...");
	unreg_keybrd();
	hint("Driver stopped");
}

module_init(init_proc);
module_exit(exit_proc);

MODULE_LICENSE( "GPL" );
MODULE_AUTHOR( "Pavel Berejnoy" );
MODULE_DESCRIPTION( DRIVER_DESC );
