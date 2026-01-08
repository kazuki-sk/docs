# 10_Network

## Definition

物理ネットワーク機器、論理ネットワーク設計、およびネットワークの根幹となるコアサービス（DNS/DHCP等）の設定を管理する。

## Scope

* **Physical**: Router (IX2215, RTX), Switch, Wi-Fi AP
* **Logical**: VLAN Design, Subnetting, IPAM
* **Core Services**: Internal DNS (Unbound/Bind), DHCP, VPN (WireGuard/Tailscale)
* **Cloud Network**: Azure VNet, AWS VPC

## Contents

* **[Squid Proxy Server](./Squid/index.md)**
  * **概要**: LAN内クライアントのHTTP/HTTPS通信制御・監視用プロキシ。
  * **機能**: Tunneling, Basic Authentication, SSL Bumping (HTTPS解析)
  * **Status**: Stable

* **[BIND9 DNS Server](./Bind/index.md)**
  * **概要**: LAN内名前解決の一元化およびカスタムドメインの権威DNS。
  * **機能**: Authoritative (Master), Forwarding, ACL Design
  * **Status**: Stable
