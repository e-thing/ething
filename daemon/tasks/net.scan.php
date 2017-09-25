<?php


include __DIR__.'/../../src/Net.php';

echo json_encode(Ething\Net::scanLocalNetwork(), JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES).PHP_EOL;

