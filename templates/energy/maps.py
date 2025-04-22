{% extends 'energy/base.html' %}
{% load custom_filters %}
{% block title %}Interactive World Map - Renewable Energy Dashboard{% endblock %}
{% block content %}
<h1 class="mb-4">Interactive World Map</h1>

{% if error %}
    <div class="alert alert-danger">{{ error }}</div>
{% else %}
    <div class="mb-4">
        <p>Click on a country to view its renewable energy data for 2015.</p>
        {{ map_html|safe }}
    </div>
    <p><a href="{% url 'energy/index' %}" class="btn btn-primary">Back to Home</a></p>
{% endif %}
{% endblock %}