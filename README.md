# housemate_backend
Docker-compose back-end for the Housemate household expenses app

## AWS SSH access

    ssh -i /c/Users/pstev/Documents/GitHub/housemate/admin/housemate_ec2.pem ubuntu@ec2-13-54-159-243.ap-southeast-2.compute.amazonaws.com

## For initdb.sh; line endings problem when writing shell scripts in Windows and running on Linux

See: https://unix.stackexchange.com/a/368399/370513

To fix, in vim:

    vim initdb.sh
    :set ff=unix
    :set nobomb
    :wq

and in Linux terminal:

    chmod 755 initdb.sh

## cron

Test cron:

    run-parts --report /etc/cron.hourly

## Remove database volume

   docker volume rm housemate_housemate_data
