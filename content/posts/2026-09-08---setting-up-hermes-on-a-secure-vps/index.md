---
title: "Setting Up Hermes on a Secure VPS"
date: "2026-09-08T00:00:00.000Z"
template: "post"
draft: true
slug: "/posts/setting-up-hermes-on-a-secure-vps"
category: "Developer Tools"
tags:
  - "AI"
  - "Developer Tools"
  - "Linux"
  - "VPS"
  - "Security"
  - "Hermes"
description: "A practical first setup for running Hermes on a Linux VPS: harden SSH before installing the agent, keep the dashboard private, and verify each change before ending your session."
---

Running a personal agent on a server is not difficult. Running one without creating a small security problem is where the work starts.

I set up [Hermes](https://hermes-agent.nousresearch.com/) on a Linux VPS because I wanted an agent that could stay available, work with my notes and tools, and communicate through Telegram. The agent itself was straightforward to install. The more important part was securing the host first.

This is the order I recommend: secure access, create a normal user, verify you can still log in, then install Hermes. Do not start by exposing a dashboard to the internet.

This is a practical record of my setup, not a universal production hardening guide. Read the current [Hermes documentation](https://hermes-agent.nousresearch.com/docs) for the latest installation and configuration instructions.

## Start with a clean, updated server

I used a small Linux VPS from Hetzner. The provider is not the important part. What matters is that you start from a fresh supported image and update it before adding services.

```bash
sudo apt update
sudo apt upgrade
```

Reboot if the upgrade requires it. Then reconnect before continuing.

## Create a normal user before disabling root access

Do not run a long-lived service as root. Create a normal account and grant it sudo access:

```bash
adduser cedric
usermod -aG sudo cedric
```

Replace `cedric` with your own username.

Next, add your public SSH key to that user. If you are starting from an existing root session that already has the right key, this is one way to copy it:

```bash
mkdir -p /home/cedric/.ssh
chmod 700 /home/cedric/.ssh
cp /root/.ssh/authorized_keys /home/cedric/.ssh/
chown -R cedric:cedric /home/cedric/.ssh
chmod 600 /home/cedric/.ssh/authorized_keys
```

Before changing SSH settings, open a **separate terminal** and confirm that the new user can log in:

```bash
ssh cedric@YOUR_SERVER_IP
```

Do not close the original session until this works. This one check prevents the most expensive mistake in a small server setup: locking yourself out remotely.

## Harden SSH carefully

Once key-based login works for the normal user, configure SSH to reject root and password logins.

Edit the server configuration:

```bash
sudo vi /etc/ssh/sshd_config
```

Make sure these settings are present and not overridden by a file under `sshd_config.d`:

```text
PubkeyAuthentication yes
PermitRootLogin no
PasswordAuthentication no
```

Validate the configuration before restarting SSH:

```bash
sudo sshd -t
```

No output means the syntax is valid. Then restart the service:

```bash
sudo systemctl restart ssh
```

Keep the first session open and test a second login again. If the new login fails, you still have a session that can undo the change.

This was the part of the setup that made me slow down. It is easy to copy a few SSH settings from a guide. It is better to understand the failure mode: one incorrect setting can remove the only path back into the machine.

## Install Hermes from the official source

After the host is reachable through the normal user, install Hermes using its official installer:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Then use the interactive setup flow to choose a model provider and check that the installation is healthy:

```bash
hermes setup
hermes doctor
```

The exact provider setup depends on what you use. Keep API keys and tokens out of shell history, repositories, and notes that are committed to Git. Hermes stores configuration and secrets separately, and its documentation covers the available providers and authentication methods.

At this point, run a simple chat locally on the server before adding integrations:

```bash
hermes
```

A boring first success is useful. It proves the installation, model configuration, and network access work before you introduce Telegram, dashboards, schedules, or your personal files.

## Keep the dashboard private

Hermes has a dashboard, but I would not expose it directly on a public IP unless I had a specific reason and a proper security plan.

For remote access, I use SSH port forwarding. Start the dashboard on the server, then create a tunnel from my own machine using the port Hermes reports when it starts:

```bash
ssh -N -L LOCAL_PORT:127.0.0.1:REMOTE_PORT cedric@YOUR_SERVER_IP
```

For example, if the dashboard is listening on port `9119` on the VPS and I want the same local port:

```bash
ssh -N -L 9119:127.0.0.1:9119 cedric@YOUR_SERVER_IP
```

The dashboard remains bound to the server's loopback interface. Only a machine that can authenticate over SSH can reach it through the tunnel.

Port forwarding works well for occasional administration. It can feel slow, though, especially when the server is far from where you actually work. That has made me reconsider the long-term placement of this system.

## My next move: keep more of it local

A VPS is convenient because it stays online. But most of my Hermes usage happens inside my home network, alongside my Obsidian vault and personal services.

I am considering moving the main instance to a Mac mini or Raspberry Pi. That should reduce latency and remove some unnecessary network distance. It also keeps the system closer to the files and services it needs to work with.

That trade-off is worth stating plainly:

- a VPS is easier to reach from anywhere, but requires more careful remote security and can add latency
- a local machine is faster for local work and simpler for local files, but needs its own approach for remote access, backups, and power reliability

There is no universal answer. The right host is the one that matches where you use the agent and how much operational work you want to own.

## The principle I would keep

Installing Hermes is the easy part. The setup becomes durable when you treat it like any other service with access to useful parts of your life:

1. use a normal account, not root
2. rely on SSH keys and test changes before closing a working session
3. keep dashboards private by default
4. add permissions and integrations gradually
5. verify each layer before adding the next one

That approach is less exciting than rushing to the dashboard. It is also how you end up with a personal agent you can keep using instead of a server you are afraid to touch.
