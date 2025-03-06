# integral_pos
Generic POS terminal based on Peter Jospeh's Integral system.

Modify to work as a generic POS system, i.e. for use with any ordering system.

Major Refactor 06/03/25 to remove Settings tab - not needed.

### Trouble Shooting
If Process is already running on Windows, here is how to stop it:
To find out which process is using a certain port in Windows and then kill it, follow these steps:

1. Find the Process Using the Port

Open Command Prompt as Administrator and run:
```
netstat -ano | findstr :8050
```

- This will return a line with details about the connection, including the Process ID (PID).
- Example output:
```
TCP    127.0.0.1:8050    0.0.0.0:0    LISTENING    1234
```
Here, 1234 is the PID of the process using port 8050.

2. Find the Process Name (Optional)

If you want to find the process name associated with the PID, run:
```
tasklist | findstr 1234
```
3. Kill the Process

To terminate the process using the port, run:
```
taskkill /PID 1234 /F
```
The /F flag forces termination.

Now, the port should be free for use again.