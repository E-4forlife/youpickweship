TODO:
more clean up
set up SMS
set up in docker
upload to AWS and point DNS


The secrets secrets / environment vars are stored in the gpg secrets file


Always encrypt the file that contains the application's secrets, you dont want your keys exposed on github.

To Use GPG:
https://www.cyberciti.biz/tips/linux-how-to-encrypt-and-decrypt-files-with-a-password.html
(despite the title of this link the file is actually encrypted with a password


Encrypting a file (will ask for password): 
gpg -c FILE_NAME

You want to do this after decrypting a file to edit ^

Decrypting a file to modify it and write to it:

gpg --decrypt FILE_NAME --output WHAT_YOU_WANT_IT_TO_BE_CALLED

This will spit out an unencrypted version of the file so you can modify it, make sure to not commit this to git,
remember to reencrypt and commit the new file with the changes.


After encrypting it does not ask me for a password to decrypt?

https://unix.stackexchange.com/questions/395875/gpg-does-not-ask-for-password



I will send you the passphrase.

