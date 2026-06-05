# SCRU

Simple Cloudflare Record Updater

## Description

Very simple CLI application to easily update IPv4 Cloudflare records from different sources.

## Platforms

The app will be released as a linux package only.

## Available commands

- `scru`: running the app with no arguments will perform the update
- `scru config`: used to create or edit the configuration

## IP update sources

- Fixed: you provide a fixed IP
- Public: scru will get the public IP of the system is running on
- Custom: custom command that will be ran to get the IP

## Tech stack

- Python
