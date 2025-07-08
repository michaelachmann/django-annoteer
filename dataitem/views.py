from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Dataitem
from .forms import DataitemForm
import csv
import io
from django.shortcuts import redirect
from .forms import CSVUploadForm
from .models import DataEntry


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


@login_required


def data_import_view(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            try:
                decoded_file = io.TextIOWrapper(file, encoding='utf-8')
                reader = csv.DictReader(decoded_file)

                # Check column headers
                if 'id' not in reader.fieldnames or 'text' not in reader.fieldnames:
                    form.add_error('file', 'CSV muss Spalten "id" und "text" enthalten.')
                    return render(request, 'dataitem/data_import.html', {'form': form})

                count_created = 0
                count_updated = 0

                for row in reader:
                    external_id = row['id']
                    text = row['text']
                    if not external_id:
                        continue
                    obj, created = DataEntry.objects.update_or_create(
                        external_id=external_id,
                        defaults={'text': text}
                    )
                    if created:
                        count_created += 1
                    else:
                        count_updated += 1

                return render(request, 'dataitem/data_import_success.html', {
                    'created': count_created,
                    'updated': count_updated
                })

            except UnicodeDecodeError:
                form.add_error('file', 'Datei konnte nicht als UTF-8 gelesen werden.')
    else:
        form = CSVUploadForm()

    return render(request, 'dataitem/data_import.html', {'form': form})