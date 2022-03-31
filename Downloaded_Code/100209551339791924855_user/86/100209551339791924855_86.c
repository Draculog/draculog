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

	char* token;

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
		else{
			// remove trailing newline
			*pos = '\0';
		
		
			//compare input string to token, if equal output 0
			token = strtok(s, ">");
			int exitToken = strcmp(token, "exit");
			int helpToken = strcmp(token, "help");
			int todayToken = strcmp(token, "today");
		
			//exit command
			if(exitToken == 0){
				//printf("\n");
				exit(0);
			}
		
			//help command
			else if(helpToken == 0){
				printf("enter Linux commands, or 'exit' to exit\n");
				continue;
			}
		
			//today command
			else if(todayToken == 0){
				time_t now;
				time(&now);
				struct tm *local = localtime(&now);
				int month = local->tm_mon + 1;
				int day = local->tm_mday;
				int year = local->tm_year + 1900;
				printf("%02d/%02d/%d\n", month, day, year);
				continue;
			
			}
			else{
				int rc = fork();
				if(rc < 0){	//fork failed;exit
					fprintf(stderr, "fork failed\n");
					exit(1);
				}
				else if(rc == 0){ //new process
					char *inputs = strtok(s, " \n");
					int count = 0;
					while(inputs){//puts inputs into an array
						toks[count] = strdup(inputs);
						count++;
						inputs = strtok(NULL, " \n");//end array
					}
					//runs command if valid, otherwise prints error
					if(execvp(toks[0], toks)){
						printf("msh: %s: %s\n", toks[0], strerror(errno));
						break;
					}	
				}
				else{
					int wc = wait(NULL);
				}
			}	
		}
	}	
	exit(EXIT_SUCCESS);
}
