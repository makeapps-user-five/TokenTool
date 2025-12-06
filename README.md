simple set of Python tools for automating token-related processes

usage : 
1. create or find and open input.txt
2. put all tokens in input.txt ( 1 token per line )
3. launch token validator
4. the result will be saved in data.db

The application takes a screenshot of the desktop to check if there is a QR code in the application. If there is a QR code in the screenshot, the account needs to be verified manually. If an account selection appears, the account has been restored.

To be honest: yes, this is absolute crap code and it may not work properly. (At least it's not VIBE code, and I know what I'm talking about). Due to the nature of how it works, there may be glitches. Once we figure out how to make requests with tokens via server requests, we'll redo the validator. But right now, it doesn't work perfectly. 
