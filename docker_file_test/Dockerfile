FROM vauxoo/odoo-80-image-shippable-auto
#Create files
#cp files/ssh
#cp files/git-prompt.sh
#cp files/git_prompt_profile
#cp files/bash_profile_psql.sh

ENV TERM xterm
ADD files/ssh /home/odoo/.ssh
# ADD files/profile /home/odoo/.profile
ADD files/git-prompt.sh /home/odoo/.git-prompt.sh
ADD files/git_prompt_profile /tmp/git_prompt_profile
ADD files/bash_profile_psql.sh /home/odoo/.bash_profile_psql.sh
RUN cat /tmp/git_prompt_profile >> /home/odoo/.profile \
    && rm /tmp/git_prompt_profile

# Install ngrok to run fowardporting in developer environment

RUN apt-get update && apt-get install curl unzip && curl https://dl.ngrok.com/ngrok_2.0.19_linux_amd64.zip -o /tmp/ngrok.zip \

    && unzip -o /tmp/ngrok.zip -d /usr/local/bin/ \
    && rm -rf /tmp/ngrok.zip

USER root
RUN chown -R odoo:odoo /home/odoo
