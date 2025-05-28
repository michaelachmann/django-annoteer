from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Dataitem
from .forms import DataitemForm


def dataitem_list(request):
    dataitems = Dataitem.objects.all()
    return render(request, "dataitems/dataitem_list.html", {"dataitems": dataitems})


def dataitem_detail(request, pk):
    dataitem = get_object_or_404(Dataitem, pk=pk)
    return render(request, "dataitems/dataitem_detail.html", {"dataitem": dataitem})


@login_required
def dataitem_create(request):
    if request.method == "POST":
        form = DataitemForm(request.POST)
        if form.is_valid():
            dataitem = form.save(commit=False)
            dataitem.created_by = request.user
            # Optionally set project here if applicable
            dataitem.save()
            return redirect("dataitems:dataitem_list")
    else:
        form = DataitemForm()
    return render(request, "dataitems/dataitem_form.html", {"form": form})


@login_required
def dataitem_update(request, pk):
    dataitem = get_object_or_404(Dataitem, pk=pk)
    form = DataitemForm(request.POST or None, instance=dataitem)
    if form.is_valid():
        form.save()
        return redirect("dataitems:dataitem_detail", pk=dataitem.pk)
    return render(request, "dataitems/dataitem_form.html", {"form": form})


@login_required
def dataitem_delete(request, pk):
    dataitem = get_object_or_404(Dataitem, pk=pk)
    if request.method == "POST":
        dataitem.delete()
        return redirect("dataitems:dataitem_list")
    return render(request, "dataitems/dataitem_confirm_delete.html", {"dataitem": dataitem})
