from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from dataitem.models import Dataitem
from .models import Project, Label
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm, LabelForm
from django.forms import inlineformset_factory

# Projektliste
def project_list(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, "projects/project_list.html", {"projects": projects})

# Projektdetailseite
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    dataitems = Dataitem.objects.filter(project=project)
    return render(request, "projects/project_detail.html", {
        "project": project,
        "dataitems": dataitems,
    })

# Projekt erstellen
@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            return redirect("projects:project_list")
    else:
        form = ProjectForm()
    return render(request, "projects/project_form.html", {"form": form})

# Projekt aktualisieren
@login_required
def project_update(request, pk):
    projects = Project.objects.filter(created_by=request.user)
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:project_list")
    else:
        error = form.errors
    return render(request, "projects/project_form.html", {"form": form, "error": error})

# Projekt löschen
@login_required
def project_delete(request, pk):
    projects = Project.objects.filter(created_by=request.user)
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        project.delete()
        return redirect("projects:project_list")
    return render(request, "projects/project_confirm_delete.html", {"project": project})

# Labelverwaltung
@login_required
def label_manage(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.created_by != request.user:
        raise PermissionDenied

    LabelFormSet = inlineformset_factory(
        Project,
        Label,
        form=LabelForm,
        fields=("label", "value"),
        extra=0,
        can_delete=True
    )



    if request.method == "POST":
        formset = LabelFormSet(request.POST or None, instance=project)
        print("POST erhalten:", request.POST)
        print(formset.errors)
        if formset.is_valid():
            for form in formset:
                print("DELETE?", form.cleaned_data.get("DELETE"),
                      "| Label:", form.cleaned_data.get("label"),
                      "| Value:", form.cleaned_data.get("value"))
            formset.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        formset = LabelFormSet(instance=project)

    return render(request, "projects/label_manage.html", {
        "project": project,
        "formset": formset
    })