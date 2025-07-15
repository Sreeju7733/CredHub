---
layout: default
title: My Professional Badges
permalink: /badges/
---

<h1>My Professional Badges</h1>

<div class="badges-grid">
  {% assign sorted_badges = site.data.badges | sort: "issued" | reverse %}
  {% for badge in sorted_badges %}
    {% include badge-card.html badge=badge %}
  {% endfor %}
</div>
