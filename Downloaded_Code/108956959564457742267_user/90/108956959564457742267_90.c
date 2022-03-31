#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <time.h>

/*
 * A very simple shell that supports only commands 'exit', 'help', and 'today'.
 */

#define MAX_BUF 160
#define MAX_TOKS 100

int main() {
	int ch;
	char *pos;
	char s[MAX_BUF+2];   // 2 extra for the newline and ending '\0'
	static const char prompt[] = "msh> ";
	char *toks[MAX_TOKS];

	// 
	// YOUR CODE HERE   (add declarations as needed)
	//

	while (1) {
		// prompt for input if input from terminal
		if (isatty(fileno(stdin))) {
			printf(prompt);
		}

		// read input
		char *status = fgets(s, MAX_BUF+2, stdin);

		// exit if ^d entered
		if (status == NULL) {
			printf("\n");
			break;
		}

		// input is too long if last character is not newline 
		if ((pos = strchr(s, '\n')) == NULL) {
			printf("error: input too long\n");
			// clear the input buffer
			while ((ch = getchar()) != '\n' && ch != EOF) ;
			continue; 
		}

		// remove trailing newline
		*pos = '\0';
		char* tokens = strtok(status, " ");
		if(!strcmp(tokens,"help")){
			printf("enter 'help', 'today', or 'exit' to quit\n");
		} else if(!strcmp(tokens,"today")){
			time_t *sinceEpoch;
			time(&sinceEpoch);
			struct tm *current;
                        current = localtime(&sinceEpoch);
			int month = current->tm_mon+1;
			int day = current->tm_mday;
			char monthBuf[3] = "";
			char dayBuf[3] = "";
			if(month < 10){
				sprintf(monthBuf, "0%d", month);
			} else {
				sprintf(monthBuf, "%d", month);
			}
			if(day < 10){
				sprintf(dayBuf, "0%d", day);
			} else{
				sprintf(dayBuf, "%d", day);
			}
			printf("%s/%s/%d\n", monthBuf, dayBuf, current->tm_year+1900);
		} else if(!strcmp(tokens,"exit")){
			break;
		} else {
			printf("token: '%s'\n", tokens);
		}
		tokens = strtok(NULL, " ");
		while(tokens != NULL) {
			printf("token: '%s'\n", tokens);
			tokens = strtok(NULL, " ");
		}
		
		//
		// YOUR CODE HERE
		//
		
	}
	exit(EXIT_SUCCESS);
}
