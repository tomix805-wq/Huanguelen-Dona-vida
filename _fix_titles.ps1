$path = "C:\Users\User\OneDrive\Desktop\Huanguelen Dona vida\index.html"
$html = [IO.File]::ReadAllText($path, [Text.UTF8Encoding]::new($false))
$html = [regex]::Replace($html, '"title":"[^"]*","id":"1HcjbWVlKzFzGxYdEmsn5pFM2Mg8hE4FF"', '"title":"Campaña Perio 2025","id":"1HcjbWVlKzFzGxYdEmsn5pFM2Mg8hE4FF"')
$html = [regex]::Replace($html, '"title":"[^"]*","id":"17SgSCBXV5tQvuyBopE6K9oNI-aS70pas"', '"title":"Cantor Orillero - Huanguelén - octubre 2026","id":"17SgSCBXV5tQvuyBopE6K9oNI-aS70pas"')
$html = [regex]::Replace($html, '"title":"[^"]*","id":"1MH3PEwoGwEiSo6Lhajkzrc5JRjB2YRUa"', '"title":"Facultad de Cs. Médicas UNLP - noviembre 2026","id":"1MH3PEwoGwEiSo6Lhajkzrc5JRjB2YRUa"')
$html = [regex]::Replace($html, '"title":"[^"]*","id":"1d9iMYNu1uxCy30wqMKG56LuDuXzlN-uy"', '"title":"Travesía por la Vida - octubre 2026","id":"1d9iMYNu1uxCy30wqMKG56LuDuXzlN-uy"')
[IO.File]::WriteAllText($path, $html, [Text.UTF8Encoding]::new($false))
Write-Output "ok"