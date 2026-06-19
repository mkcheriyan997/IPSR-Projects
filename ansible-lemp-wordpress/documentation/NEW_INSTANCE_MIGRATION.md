# Task #49310 New Instance Migration

## New AWS target

- Instance ID: `i-02f9968c4d07985a1`
- Region: `eu-north-1`
- Instance type: `t3.small`
- Elastic IP: `13.51.76.196`
- Ansible host: `wordpress_new`
- SSH user: `ec2-user`

The complete WordPress stack is deployed on the new instance. Public DNS was
updated to the new Elastic IP on 2026-06-19.

## DNS and TLS cutover

The cutover is complete. Public DNS resolves to `13.51.76.196`, HTTPS is
canonical, and the Let's Encrypt renewal timer is active.

1. Public DNS for `mlolad.xyz` must return `13.51.76.196`.
2. `inventory.ini` must contain `enable_tls=true`.
3. From this directory, run:

   ```bash
   ansible-playbook setup_wordpress.yml
   ```

The final run obtains the Let's Encrypt certificate on the new instance,
changes WordPress `home` and `siteurl` to HTTPS, redirects HTTP to HTTPS, and
keeps `certbot-renew.timer` enabled.

Public HTTPS checks against `https://mlolad.xyz/`, `/wp-admin/`, and
`/phpmyadmin/` have passed.
