# Tynk Cluster node starter/status checker
# This script is meant to be run automatically on every set interval per server.
# It will attempt to detect if the cluster node is running or not, and if the node is not running, then check connection to discord and then act based on that.
# Conditions: discordapp.com must be reachable, and the bot must not already be running.
# If the conditions are met, then the script will attempt to start the bot.


# Location of the bot script.
$botPath = "C:\Users\Administrator\Dropbox\Bots\Tynk"

# First step is to check if the node is running. There is an if block for each node, but I believe it could be merged to one?
function CheckProcesses {
    if ($env:COMPUTERNAME -eq "DINOSAURASSSSSS") {
        $localNode = "Rubert"
        # Searches the open processes
        $ProcessSearch = Get-Process | Where-Object {($_.MainWindowTitle -ne "" -and $_.MainWindowTitle -eq $localNode)} | Select-Object -ExpandProperty MainWindowTitle
        $ProcessSearch | ForEach-Object {
            # If the node process is running, then it will terminate the whole script, as the point of this script is to start the bot if it is not open.
            if ($_ -eq $localNode) {
                Write-Host "The node process is running."
                $return = "True"
                return $return
            }
        }
    }
    elseif ($env:COMPUTERNAME -eq "DOGGO-PLS") {
        $localNode = "Robert"
        # Searches the open processes
        $ProcessSearch = Get-Process | Where-Object {($_.MainWindowTitle -ne "" -and $_.MainWindowTitle -eq $localNode)} | Select-Object -ExpandProperty MainWindowTitle
        $ProcessSearch | ForEach-Object {
            # If the node process is running, then it will terminate the whole script, as the point of this script is to start the bot if it is not open.
            if ($_ -eq $localNode) {
                Write-Host "The node process is running."
                $return = "True"
                return $return
            }
        }
    }

    else {
        Write-Host "Local machine is not part of the node. Exiting"
        Exit
    }
}
#Checks the connection to Discord
function CheckConnection {
    # Creates the HTTP request and gets the response, and converts the status code into a integer.
    $HTTP_Request = [System.Net.WebRequest]::Create('http://discordapp.com')
    $HTTP_Response = $HTTP_Request.GetResponse()
    $HTTP_Status = [int]$HTTP_Response.StatusCode

    if ($HTTP_Status -eq 200) {
        $return = "True"
        return $return
    }
    else {
        $return = "False"
        return $return
    } 
}
# Main Script
# Checks process to see if its running. If true, exit the script. Nothing else for the script to do.
if ((CheckProcesses) -eq "True") {
    Write-Host "Exiting..."
    Exit
}
# Otherwise it will continue to check the connection. If no connection can be made, then exit the script, as either the server is down or the host is.
# There isn't anything else for the script to do in that case.
# If the connection can be made, then start the script again.
else {
    if ((CheckConnection) -ne "True") {
        Write-Host "Connection cannot be made. Exiting..."
        Exit
    }
    else {
        Set-Location $botPath
        if ($env:COMPUTERNAME -eq "DINOSAURASSSSSS") {
            Invoke-Item "Rubert.lnk"
        }
        elseif ($env:COMPUTERNAME -eq "DOGGO-PLS") {
            Invoke-Item "Robert.lnk"
        }
    }
}

Write-Host "Script complete."
