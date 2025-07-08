# projects/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from dataitem.models import Dataitem
from .models import Project
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm

def project_list(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, "projects/project_list.html", {"projects": projects})


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    dataitems = Dataitem.objects.filter(project=project)
    return render(request, "projects/project_detail.html", {
        "project": project,
        "dataitems": dataitems,
    })



@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            return redirect("projects:project_list") # redirect auf Labelverwaltung
    else:
        form = ProjectForm()
    return render(request, "projects/project_form.html", {"form": form})


@login_required
def project_update(request, pk):
    projects = Project.objects.filter(created_by=request.user)
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:project_list") # redirect auf Labelverwaltung
    else:
        error = form.errors # check if correct
    return render(request, "projects/project_form.html", {"form": form, "error": error})



@login_required
def project_delete(request, pk):
    projects = Project.objects.filter(created_by=request.user)
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        project.delete()
        return redirect("projects:project_list")
    return render(request, "projects/project_confirm_delete.html", {"project": project})


from django.forms import inlineformset_factory
from .models import Project, Label
from .forms import LabelForm  # musst du ggf. noch erstellen

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
        extra=1,
        can_delete=True
    )

    formset = LabelFormSet(request.POST or None, instance=project)

    if request.method == "POST" and formset.is_valid():
        formset.save()
        return redirect("projects:project_detail", pk=project.pk)

    return render(request, "projects/label_manage.html", {
        "project": project,
        "formset": formset
    })