<h1 align="center">🐧 DistroHop</h1>
<h3 align="center">Cross-Distro Backup & Restore</h3>

<div align="center">
  <strong>Backup your files + configs + apps → Restore on any Linux distro</strong><br>
  Supports Debian/Ubuntu • Fedora/RHEL • Arch • Derivatives
</div>

<br>

<h2>✨ Features</h2>
<ul>
  <li>📦 Backs up home files (Documents, configs, etc.)</li>
  <li>📋 Saves installed apps (APT/DNF/Pacman/Flatpak)</li>
  <li>🔄 Restores apps using target system's package manager automatically</li>
  <li>💾 Creates single-file USB backups</li>
</ul>

<h2>🔧 Usage</h2>
<h3>Export Backup</h3>
<ol>
  <li>Insert USB → Select files/apps → Create backup</li>
</ol>

<h3>Import Restore</h3>
<ol>
  <li>Insert backup USB → Restore files → Reinstall same apps</li>
</ol>

<h2>📌 Supported Systems</h2>
<table>
  <tr>
    <th>Package Manager</th>
    <th>Distros</th>
  </tr>
  <tr>
    <td>APT</td>
    <td>Debian, Ubuntu</td>
  </tr>
  <tr>
    <td>DNF/Yum</td>
    <td>Fedora, RHEL</td>
  </tr>
  <tr>
    <td>Pacman</td>
    <td>Arch, Manjaro</td>
  </tr>
</table>

<h2>⚠️ Notes</h2>
<ul>
  <li>Requires Python 3.6+ and basic CLI tools</li>
  <li>Root access needed for app installation</li>
  <li>Package names must match between distros</li>
</ul>
