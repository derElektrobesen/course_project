#ifndef MAIN_HEADER_H
#define MAIN_HEADER_H

#include <linux/module.h>
#include <linux/kernel.h>
#include <asm/param.h>		/* HZ */

/**
  * Используется для вывода сообщений в лог файл
  */
#ifndef TARGET
#	define TARGET		"Keyboard_filter_driver"
#endif

/**
  * Описание драйвера
  */
#ifndef DRIVER_DESC
#	define DRIVER_DESC	"Simple keyboard driver filter."
#endif

/**
  * Максимальная задержка для клавиши
  */
#ifndef MAX_DELAY_USEC
#	define MAX_DELAY_USEC	700
#endif
#define MAX_DELAY			(MAX_DELAY_USEC * HZ / 1000)

/**
  * Строка для вывода сообщений в лог
  */
#define NOTICE			TARGET " notice: "

/**
  * Макрос позволяет выводить в лог
  * дебаг информацию
  */
#define _log(format, ...) \
	printk(KERN_INFO NOTICE format "\n", ## __VA_ARGS__)
#define log(format, ...) _log(format, ##__VA_ARGS__)
#define perror(format, ...) \
	printk(KERN_ERR NOTICE format "\n", ## __VA_ARGS__)
#define hint(format, ...) \
	_log(format, ## __VA_ARGS__)
#ifndef DEBUG
#	undef log
#	define log(format, ...)
#endif

/**
  * Макрос позволяет логировать факт невыполнения
  * условия. Используется только в DEBUG сборке
  */
#ifdef DEBUG
#	define assert(condition) \
		if (!(condition)) \
		{ \
			log("Assertion (%s): %s, %s, line %d", \
				#condition, __FILE__, __FUNCTION__, \
				__LINE__); \
		}
#else
#	define assert(condition)
#endif

#endif
